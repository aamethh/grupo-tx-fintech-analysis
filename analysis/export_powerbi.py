"""
export_powerbi.py
-----------------
Builds three flat, dashboard-ready CSV files for Power BI:
  1. dashboard/financials_flat.csv     — all annual figures
  2. dashboard/metrics_flat.csv        — all calculated ratios (%)
  3. dashboard/timeseries_aum.csv      — monthly AUM trend
"""
import pandas as pd
from sqlalchemy import text
from db_connect import get_engine

OUT = {
    "financials":  "dashboard/financials_flat.csv",
    "metrics":     "dashboard/metrics_flat.csv",
    "timeseries":  "dashboard/timeseries_aum.csv",
}


def export_financials(engine):
    query = """
        SELECT
            c.company_code          AS Company,
            c.company_name          AS CompanyName,
            c.sector                AS Sector,
            f.fiscal_year           AS Year,
            f.total_assets   / 1e6  AS TotalAssets_M,
            f.gross_loans    / 1e6  AS GrossLoans_M,
            f.total_deposits / 1e6  AS Deposits_M,
            f.total_equity   / 1e6  AS Equity_M,
            f.aum            / 1e6  AS AUM_M,
            f.net_income     / 1e6  AS NetIncome_M,
            f.net_revenue    / 1e6  AS Revenue_M,
            f.fee_income     / 1e6  AS FeeIncome_M,
            f.interest_income/ 1e6  AS InterestIncome_M,
            f.capital_ratio  * 100  AS CapitalRatio_Pct,
            f.npl_ratio      * 100  AS NPL_Ratio_Pct,
            f.npl_coverage   * 100  AS NPL_Coverage_Pct
        FROM financials f
        JOIN companies  c ON c.company_id = f.company_id
        ORDER BY c.company_code, f.fiscal_year
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    df.to_csv(OUT["financials"], index=False)
    print(f"  Exported {len(df)} rows -> {OUT['financials']}")
    return df


def export_metrics(engine):
    query = """
        SELECT
            c.company_code                  AS Company,
            m.fiscal_year                   AS Year,
            ROUND(m.roe            * 100, 2) AS ROE_Pct,
            ROUND(m.roa            * 100, 2) AS ROA_Pct,
            ROUND(m.nim            * 100, 2) AS NIM_Pct,
            ROUND(m.cost_to_income * 100, 2) AS CostToIncome_Pct,
            ROUND(m.loan_to_deposit* 100, 2) AS LoanToDeposit_Pct,
            ROUND(m.capital_multiplier, 2)   AS CapitalMultiplier,
            ROUND(m.aum_to_assets  * 100, 2) AS AUM_to_Assets_Pct,
            ROUND(m.aum_to_loans   * 100, 2) AS AUM_to_Loans_Pct,
            ROUND(m.aum_growth_yoy * 100, 2) AS AUM_Growth_YoY_Pct,
            ROUND(m.asset_growth_yoy*100, 2) AS Asset_Growth_YoY_Pct,
            ROUND(m.income_growth_yoy*100,2) AS Income_Growth_YoY_Pct
        FROM metrics m
        JOIN companies c ON c.company_id = m.company_id
        ORDER BY c.company_code, m.fiscal_year
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    df.to_csv(OUT["metrics"], index=False)
    print(f"  Exported {len(df)} rows -> {OUT['metrics']}")
    return df


def export_timeseries(engine):
    query = """
        SELECT
            c.company_code              AS Company,
            ts.period_date              AS Date,
            FORMAT(ts.period_date,'MMM yyyy') AS Period,
            ts.metric_name              AS Metric,
            ts.metric_value / 1e6       AS Value_M,
            ROUND(
                (ts.metric_value
                 - LAG(ts.metric_value) OVER (PARTITION BY ts.company_id ORDER BY ts.period_date))
                / NULLIF(LAG(ts.metric_value) OVER (PARTITION BY ts.company_id ORDER BY ts.period_date),0)
                * 100, 2
            ) AS MoM_Growth_Pct
        FROM time_series ts
        JOIN companies   c ON c.company_id = ts.company_id
        WHERE ts.metric_name = 'aum'
        ORDER BY ts.company_id, ts.period_date
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    df.to_csv(OUT["timeseries"], index=False)
    print(f"  Exported {len(df)} rows -> {OUT['timeseries']}")
    return df


if __name__ == "__main__":
    engine = get_engine()
    print("Exporting Power BI datasets...")
    export_financials(engine)
    export_metrics(engine)
    export_timeseries(engine)
    print("All exports complete.")
