-- ============================================================
-- Grupo TX  |  Financial Analysis Database
-- Schema: financials, metrics, time_series
-- ============================================================

CREATE DATABASE GrupoTX;
GO
USE GrupoTX;
GO

-- ------------------------------------------------------------
-- 1. COMPANIES
--    Master table — one row per entity being tracked
-- ------------------------------------------------------------
CREATE TABLE companies (
    company_id      INT IDENTITY(1,1) PRIMARY KEY,
    company_code    VARCHAR(10)  NOT NULL UNIQUE,   -- e.g. 'GTX'
    company_name    VARCHAR(100) NOT NULL,
    sector          VARCHAR(50),
    country         VARCHAR(50)  DEFAULT 'Panama',
    currency        CHAR(3)      DEFAULT 'USD',
    created_at      DATETIME     DEFAULT GETDATE()
);

-- ------------------------------------------------------------
-- 2. FINANCIALS
--    Annual balance sheet + P&L figures (in thousands USD)
-- ------------------------------------------------------------
CREATE TABLE financials (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    company_id          INT          NOT NULL REFERENCES companies(company_id),
    fiscal_year         SMALLINT     NOT NULL,             -- e.g. 2023
    period_type         CHAR(1)      DEFAULT 'A',          -- A=Annual, Q=Quarterly

    -- Balance Sheet
    total_assets        DECIMAL(18,2),
    total_liabilities   DECIMAL(18,2),
    total_equity        DECIMAL(18,2),
    gross_loans         DECIMAL(18,2),
    investments         DECIMAL(18,2),
    total_deposits      DECIMAL(18,2),
    aum                 DECIMAL(18,2),

    -- P&L
    net_revenue         DECIMAL(18,2),
    operating_expenses  DECIMAL(18,2),
    net_income          DECIMAL(18,2),
    interest_income     DECIMAL(18,2),
    fee_income          DECIMAL(18,2),

    -- Risk
    npl_ratio           DECIMAL(6,4),    -- e.g. 0.0215 = 2.15%
    npl_coverage        DECIMAL(6,4),    -- e.g. 1.2430 = 124.3%
    capital_ratio       DECIMAL(6,4),

    created_at          DATETIME         DEFAULT GETDATE(),

    CONSTRAINT uq_financials UNIQUE (company_id, fiscal_year, period_type)
);

-- ------------------------------------------------------------
-- 3. METRICS
--    Calculated ratios — derived from financials, stored here
--    for fast Power BI querying without recalculating each time
-- ------------------------------------------------------------
CREATE TABLE metrics (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    company_id          INT          NOT NULL REFERENCES companies(company_id),
    fiscal_year         SMALLINT     NOT NULL,

    -- Profitability
    roe                 DECIMAL(8,4),    -- Return on Equity
    roa                 DECIMAL(8,4),    -- Return on Assets
    nim                 DECIMAL(8,4),    -- Net Interest Margin
    cost_to_income      DECIMAL(8,4),

    -- Efficiency & Structure
    loan_to_deposit     DECIMAL(8,4),
    capital_multiplier  DECIMAL(8,4),

    -- AUM
    aum_to_assets       DECIMAL(8,4),
    aum_to_loans        DECIMAL(8,4),
    aum_growth_yoy      DECIMAL(8,4),

    -- Growth
    asset_growth_yoy    DECIMAL(8,4),
    loan_growth_yoy     DECIMAL(8,4),
    income_growth_yoy   DECIMAL(8,4),

    calculated_at       DATETIME         DEFAULT GETDATE(),

    CONSTRAINT uq_metrics UNIQUE (company_id, fiscal_year)
);

-- ------------------------------------------------------------
-- 4. TIME_SERIES
--    Monthly or quarterly snapshots for trend analysis
-- ------------------------------------------------------------
CREATE TABLE time_series (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    company_id      INT         NOT NULL REFERENCES companies(company_id),
    period_date     DATE        NOT NULL,              -- first day of period
    period_type     VARCHAR(10) DEFAULT 'monthly',     -- monthly / quarterly
    metric_name     VARCHAR(50) NOT NULL,              -- e.g. 'aum', 'net_income'
    metric_value    DECIMAL(18,2),

    CONSTRAINT uq_timeseries UNIQUE (company_id, period_date, metric_name)
);

-- Indexes for query performance
CREATE INDEX ix_financials_year    ON financials  (company_id, fiscal_year);
CREATE INDEX ix_metrics_year       ON metrics     (company_id, fiscal_year);
CREATE INDEX ix_timeseries_date    ON time_series (company_id, period_date);
GO
