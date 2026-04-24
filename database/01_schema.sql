-- ============================================================
-- Grupo TX  |  Financial Analysis Database  (v2 — real data)
-- Reflects actual structure from grupo_tx_financials.xlsx
-- ============================================================

CREATE DATABASE GrupoTX;
GO
USE GrupoTX;
GO

-- ------------------------------------------------------------
-- 1. FINANCIALS  (P&L + Balance Sheet)
--    Source: 2.xlsx → "Tabla Maestra" and "base de datos"
-- ------------------------------------------------------------
CREATE TABLE financials (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    fiscal_year         VARCHAR(10)  NOT NULL,    -- '2023', '2024', '2025 Q2'
    period_type         VARCHAR(10)  DEFAULT 'Annual',

    -- Income Statement
    ingresos_totales    DECIMAL(18,2),   -- Total Revenue
    costo_ventas        DECIMAL(18,2),   -- Cost of Sales (COGS)
    utilidad_bruta      DECIMAL(18,2),   -- Gross Profit
    ebitda              DECIMAL(18,2),
    ebit                DECIMAL(18,2),
    utilidad_neta       DECIMAL(18,2),   -- Net Income
    gastos_financieros  DECIMAL(18,2),   -- Interest Expense
    nopat               DECIMAL(18,2),   -- Net Operating Profit After Tax

    -- Balance Sheet
    activos_totales     DECIMAL(18,2),   -- Total Assets
    activo_corriente    DECIMAL(18,2),   -- Current Assets
    pasivo_corriente    DECIMAL(18,2),   -- Current Liabilities
    pasivo_no_corriente DECIMAL(18,2),   -- Non-Current Liabilities
    total_pasivos       DECIMAL(18,2),   -- Total Liabilities
    patrimonio          DECIMAL(18,2),   -- Equity
    deuda_total         DECIMAL(18,2),   -- Total Debt
    dias_inventario     DECIMAL(8,2),
    dias_cxc            DECIMAL(8,2),    -- Days Sales Outstanding
    dias_cxp            DECIMAL(8,2),    -- Days Payable Outstanding

    created_at          DATETIME DEFAULT GETDATE(),

    CONSTRAINT uq_financials UNIQUE (fiscal_year)
);

-- ------------------------------------------------------------
-- 2. MARGINS
--    Source: margenes.xlsx → "Hoja1"
-- ------------------------------------------------------------
CREATE TABLE margins (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    fiscal_year         VARCHAR(10)  NOT NULL,

    margen_bruto        DECIMAL(8,4),    -- Gross Margin %
    margen_ebitda       DECIMAL(8,4),    -- EBITDA Margin %
    margen_ebit         DECIMAL(8,4),    -- EBIT / Operating Margin %
    margen_neto         DECIMAL(8,4),    -- Net Margin %

    created_at          DATETIME DEFAULT GETDATE(),

    CONSTRAINT uq_margins UNIQUE (fiscal_year)
);

-- ------------------------------------------------------------
-- 3. RATIOS
--    Source: 2.xlsx → "Ratios"
-- ------------------------------------------------------------
CREATE TABLE ratios (
    id                      INT IDENTITY(1,1) PRIMARY KEY,
    fiscal_year             VARCHAR(10)  NOT NULL,

    -- Liquidity
    razon_circulante        DECIMAL(8,4),   -- Current Ratio
    prueba_acida            DECIMAL(8,4),   -- Quick Ratio
    capital_trabajo         DECIMAL(18,2),  -- Working Capital

    -- Leverage
    deuda_equity            DECIMAL(8,4),   -- D/E Ratio
    deuda_activos           DECIMAL(8,4),   -- Debt / Assets
    pct_deuda               DECIMAL(8,4),   -- Debt % of capital structure
    pct_patrimonio          DECIMAL(8,4),   -- Equity % of capital structure

    -- Coverage
    cobertura_intereses     DECIMAL(8,4),   -- Interest Coverage (EBIT / Int. Exp.)

    -- Cost of Capital
    wacc                    DECIMAL(8,4),

    created_at              DATETIME DEFAULT GETDATE(),

    CONSTRAINT uq_ratios UNIQUE (fiscal_year)
);

-- ------------------------------------------------------------
-- 4. METRICS  (derived — calculated by Python, stored here)
-- ------------------------------------------------------------
CREATE TABLE metrics (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    fiscal_year         VARCHAR(10) NOT NULL,

    -- Growth (YoY)
    revenue_growth      DECIMAL(8,4),
    ebitda_growth       DECIMAL(8,4),
    net_income_growth   DECIMAL(8,4),
    asset_growth        DECIMAL(8,4),

    -- Profitability
    roe                 DECIMAL(8,4),    -- Net Income / Equity
    roa                 DECIMAL(8,4),    -- Net Income / Total Assets
    roce                DECIMAL(8,4),    -- EBIT / Capital Employed

    -- Efficiency
    ccc                 DECIMAL(8,2),    -- Cash Conversion Cycle

    calculated_at       DATETIME DEFAULT GETDATE(),

    CONSTRAINT uq_metrics UNIQUE (fiscal_year)
);

-- ------------------------------------------------------------
-- 5. TIME_SERIES  (for trend / dashboard use)
-- ------------------------------------------------------------
CREATE TABLE time_series (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    fiscal_year     VARCHAR(10)  NOT NULL,
    metric_name     VARCHAR(50)  NOT NULL,
    metric_value    DECIMAL(18,4),

    CONSTRAINT uq_ts UNIQUE (fiscal_year, metric_name)
);

-- Indexes
CREATE INDEX ix_ts_metric ON time_series (metric_name, fiscal_year);
GO
