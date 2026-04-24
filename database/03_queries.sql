-- ============================================================
-- Grupo TX  |  Analysis Queries
-- ============================================================
USE GrupoTX;
GO

-- ------------------------------------------------------------
-- Q1. Full financials snapshot — latest year per company
-- ------------------------------------------------------------
SELECT
    c.company_code,
    c.company_name,
    f.fiscal_year,
    f.total_assets       / 1000.0  AS assets_M,
    f.gross_loans        / 1000.0  AS loans_M,
    f.total_deposits     / 1000.0  AS deposits_M,
    f.aum                / 1000.0  AS aum_M,
    f.net_income         / 1000.0  AS net_income_M,
    f.capital_ratio      * 100     AS capital_ratio_pct,
    f.npl_coverage       * 100     AS npl_coverage_pct
FROM financials f
JOIN companies  c ON c.company_id = f.company_id
WHERE f.fiscal_year = (
    SELECT MAX(f2.fiscal_year)
    FROM financials f2
    WHERE f2.company_id = f.company_id
)
ORDER BY f.total_assets DESC;

-- ------------------------------------------------------------
-- Q2. Calculated ratios inline (no metrics table needed)
-- ------------------------------------------------------------
SELECT
    c.company_code,
    f.fiscal_year,
    ROUND(f.net_income  / NULLIF(f.total_equity, 0) * 100, 2)  AS roe_pct,
    ROUND(f.net_income  / NULLIF(f.total_assets, 0) * 100, 2)  AS roa_pct,
    ROUND(f.gross_loans / NULLIF(f.total_deposits,0) * 100, 2) AS loan_to_deposit_pct,
    ROUND(f.aum         / NULLIF(f.total_assets, 0) * 100, 2)  AS aum_to_assets_pct,
    ROUND(f.operating_expenses / NULLIF(f.net_revenue, 0) * 100, 2) AS cost_to_income_pct,
    ROUND(f.total_assets / NULLIF(f.total_equity, 0), 2)        AS capital_multiplier
FROM financials f
JOIN companies  c ON c.company_id = f.company_id
ORDER BY c.company_code, f.fiscal_year;

-- ------------------------------------------------------------
-- Q3. Year-over-year growth per company
-- ------------------------------------------------------------
SELECT
    c.company_code,
    f.fiscal_year,
    ROUND(
        (f.total_assets - LAG(f.total_assets) OVER (PARTITION BY f.company_id ORDER BY f.fiscal_year))
        / NULLIF(LAG(f.total_assets) OVER (PARTITION BY f.company_id ORDER BY f.fiscal_year), 0) * 100
    , 2) AS asset_growth_yoy_pct,
    ROUND(
        (f.aum - LAG(f.aum) OVER (PARTITION BY f.company_id ORDER BY f.fiscal_year))
        / NULLIF(LAG(f.aum) OVER (PARTITION BY f.company_id ORDER BY f.fiscal_year), 0) * 100
    , 2) AS aum_growth_yoy_pct,
    ROUND(
        (f.net_income - LAG(f.net_income) OVER (PARTITION BY f.company_id ORDER BY f.fiscal_year))
        / NULLIF(LAG(f.net_income) OVER (PARTITION BY f.company_id ORDER BY f.fiscal_year), 0) * 100
    , 2) AS income_growth_yoy_pct
FROM financials f
JOIN companies  c ON c.company_id = f.company_id
ORDER BY c.company_code, f.fiscal_year;

-- ------------------------------------------------------------
-- Q4. AUM monthly trend — for Power BI line chart
-- ------------------------------------------------------------
SELECT
    c.company_code,
    ts.period_date,
    FORMAT(ts.period_date, 'MMM yyyy')  AS period_label,
    ts.metric_value                     AS aum_value,
    ROUND(
        (ts.metric_value - LAG(ts.metric_value) OVER (PARTITION BY ts.company_id ORDER BY ts.period_date))
        / NULLIF(LAG(ts.metric_value) OVER (PARTITION BY ts.company_id ORDER BY ts.period_date), 0) * 100
    , 2) AS mom_growth_pct
FROM time_series ts
JOIN companies   c ON c.company_id = ts.company_id
WHERE ts.metric_name = 'aum'
ORDER BY ts.company_id, ts.period_date;

-- ------------------------------------------------------------
-- Q5. Peer comparison — all companies, all years
-- ------------------------------------------------------------
SELECT
    c.company_code,
    f.fiscal_year,
    ROUND(f.net_income / NULLIF(f.total_equity, 0) * 100, 2)  AS roe,
    ROUND(f.net_income / NULLIF(f.total_assets, 0) * 100, 2)  AS roa,
    ROUND(f.aum        / NULLIF(f.total_assets, 0) * 100, 2)  AS aum_penetration,
    f.capital_ratio * 100                                       AS capital_ratio,
    f.npl_coverage  * 100                                       AS npl_coverage
FROM financials f
JOIN companies  c ON c.company_id = f.company_id
ORDER BY f.fiscal_year, roe DESC;
GO
