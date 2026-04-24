"""
ratios.py
---------
Pulls financials from SQL Server, calculates all ratios,
writes results back to the metrics table, and exports CSV.
"""
import pandas as pd
from sqlalchemy import text
from db_connect import get_engine

EXPORT_PATH = "outputs/metrics.csv"


def fetch_financials() -> pd.DataFrame:
    engine = get_engine()
    query = """
        SELECT
            c.company_code,
            c.company_name,
            f.fiscal_year,
            f.total_assets,
            f.total_liabilities,
            f.total_equity,
            f.gross_loans,
            f.investments,
            f.total_deposits,
            f.aum,
            f.net_revenue,
            f.operating_expenses,
            f.net_income,
            f.interest_income,
            f.fee_income,
            f.npl_ratio,
            f.npl_coverage,
            f.capital_ratio,
            f.company_id
        FROM financials f
        JOIN companies  c ON c.company_id = f.company_id
        ORDER BY c.company_code, f.fiscal_year
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def calculate_ratios(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # Profitability
    d["roe"]            = d["net_income"]  / d["total_equity"].replace(0, pd.NA)
    d["roa"]            = d["net_income"]  / d["total_assets"].replace(0, pd.NA)
    d["nim"]            = d["interest_income"] / d["total_assets"].replace(0, pd.NA)
    d["cost_to_income"] = d["operating_expenses"] / d["net_revenue"].replace(0, pd.NA)

    # Structure
    d["loan_to_deposit"]    = d["gross_loans"]   / d["total_deposits"].replace(0, pd.NA)
    d["capital_multiplier"] = d["total_assets"]  / d["total_equity"].replace(0, pd.NA)

    # AUM
    d["aum_to_assets"] = d["aum"] / d["total_assets"].replace(0, pd.NA)
    d["aum_to_loans"]  = d["aum"] / d["gross_loans"].replace(0, pd.NA)

    # YoY growth (per company)
    d = d.sort_values(["company_code", "fiscal_year"])
    for col, out in [
        ("aum",          "aum_growth_yoy"),
        ("total_assets", "asset_growth_yoy"),
        ("net_income",   "income_growth_yoy"),
    ]:
        d[out] = d.groupby("company_code")[col].pct_change()

    ratio_cols = [
        "roe", "roa", "nim", "cost_to_income",
        "loan_to_deposit", "capital_multiplier",
        "aum_to_assets", "aum_to_loans",
        "aum_growth_yoy", "asset_growth_yoy", "income_growth_yoy"
    ]
    d[ratio_cols] = d[ratio_cols].round(4)
    return d


def write_metrics_to_db(df: pd.DataFrame):
    engine = get_engine()
    ratio_cols = [
        "roe", "roa", "nim", "cost_to_income",
        "loan_to_deposit", "capital_multiplier",
        "aum_to_assets", "aum_to_loans",
        "aum_growth_yoy", "asset_growth_yoy", "income_growth_yoy"
    ]
    with engine.begin() as conn:
        for _, row in df.iterrows():
            existing = conn.execute(
                text("SELECT id FROM metrics WHERE company_id=:cid AND fiscal_year=:yr"),
                {"cid": int(row["company_id"]), "yr": int(row["fiscal_year"])}
            ).fetchone()

            vals = {col: (None if pd.isna(row[col]) else float(row[col]))
                    for col in ratio_cols}
            vals.update({"cid": int(row["company_id"]), "yr": int(row["fiscal_year"])})

            if existing:
                set_clause = ", ".join([f"{c}=:{c}" for c in ratio_cols])
                conn.execute(
                    text(f"UPDATE metrics SET {set_clause} WHERE company_id=:cid AND fiscal_year=:yr"),
                    vals
                )
            else:
                cols   = "company_id, fiscal_year, " + ", ".join(ratio_cols)
                params = ":cid, :yr, " + ", ".join([f":{c}" for c in ratio_cols])
                conn.execute(text(f"INSERT INTO metrics ({cols}) VALUES ({params})"), vals)

    print(f"Metrics written to DB for {len(df)} rows.")


def export_csv(df: pd.DataFrame):
    display_cols = [
        "company_code", "fiscal_year",
        "roe", "roa", "nim", "cost_to_income",
        "loan_to_deposit", "capital_multiplier",
        "aum_to_assets", "aum_to_loans",
        "aum_growth_yoy", "asset_growth_yoy", "income_growth_yoy"
    ]
    out = df[display_cols].copy()
    pct_cols = [
        "roe", "roa", "nim", "cost_to_income",
        "loan_to_deposit", "aum_to_assets", "aum_to_loans",
        "aum_growth_yoy", "asset_growth_yoy", "income_growth_yoy"
    ]
    for col in pct_cols:
        out[col] = (out[col] * 100).round(2)

    out.to_csv(EXPORT_PATH, index=False)
    print(f"Exported -> {EXPORT_PATH}")
    return out


if __name__ == "__main__":
    print("Fetching financials from DB...")
    df = fetch_financials()
    print(f"  {len(df)} rows loaded")

    print("Calculating ratios...")
    df = calculate_ratios(df)

    print("Writing to metrics table...")
    write_metrics_to_db(df)

    print("Exporting CSV...")
    result = export_csv(df)
    print(result.to_string(index=False))
