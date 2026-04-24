-- ============================================================
-- Grupo TX  |  Analysis Queries
-- ============================================================
USE GrupoTX;
GO

-- ------------------------------------------------------------
-- Q1. Full P&L Summary
-- ------------------------------------------------------------
SELECT
    fiscal_year                                         AS Year,
    ingresos_totales   / 1e6                            AS Revenue_M,
    costo_ventas       / 1e6                            AS COGS_M,
    utilidad_bruta     / 1e6                            AS GrossProfit_M,
    ebitda             / 1e6                            AS EBITDA_M,
    ebit               / 1e6                            AS EBIT_M,
    utilidad_neta      / 1e6                            AS NetIncome_M,
    nopat              / 1e6                            AS NOPAT_M
FROM financials
ORDER BY fiscal_year;

-- ------------------------------------------------------------
-- Q2. Margin evolution — joins financials + margins
-- ------------------------------------------------------------
SELECT
    f.fiscal_year                                       AS Year,
    f.ingresos_totales / 1e6                            AS Revenue_M,
    ROUND(m.margen_bruto   * 100, 2)                    AS GrossMargin_Pct,
    ROUND(m.margen_ebitda  * 100, 2)                    AS EBITDAMargin_Pct,
    ROUND(m.margen_ebit    * 100, 2)                    AS EBITMargin_Pct,
    ROUND(m.margen_neto    * 100, 2)                    AS NetMargin_Pct
FROM financials f
JOIN margins    m ON m.fiscal_year = f.fiscal_year
ORDER BY f.fiscal_year;

-- ------------------------------------------------------------
-- Q3. YoY Revenue & Profit Growth
-- ------------------------------------------------------------
SELECT
    fiscal_year,
    ingresos_totales / 1e6                              AS Revenue_M,
    ROUND(
        (ingresos_totales - LAG(ingresos_totales) OVER (ORDER BY fiscal_year))
        / NULLIF(LAG(ingresos_totales) OVER (ORDER BY fiscal_year), 0) * 100
    , 2)                                                AS Revenue_Growth_Pct,
    ROUND(
        (ebitda - LAG(ebitda) OVER (ORDER BY fiscal_year))
        / NULLIF(LAG(ebitda) OVER (ORDER BY fiscal_year), 0) * 100
    , 2)                                                AS EBITDA_Growth_Pct,
    ROUND(
        (utilidad_neta - LAG(utilidad_neta) OVER (ORDER BY fiscal_year))
        / NULLIF(LAG(utilidad_neta) OVER (ORDER BY fiscal_year), 0) * 100
    , 2)                                                AS NetIncome_Growth_Pct
FROM financials
ORDER BY fiscal_year;

-- ------------------------------------------------------------
-- Q4. Leverage & Liquidity overview
-- ------------------------------------------------------------
SELECT
    r.fiscal_year                                       AS Year,
    ROUND(r.razon_circulante, 2)                        AS CurrentRatio,
    ROUND(r.prueba_acida,     2)                        AS QuickRatio,
    r.capital_trabajo / 1e6                             AS WorkingCapital_M,
    ROUND(r.deuda_equity,     2)                        AS DE_Ratio,
    ROUND(r.deuda_activos * 100, 1)                     AS Debt_Assets_Pct,
    ROUND(r.cobertura_intereses, 2)                     AS InterestCoverage,
    ROUND(r.wacc * 100, 2)                              AS WACC_Pct
FROM ratios r
ORDER BY r.fiscal_year;

-- ------------------------------------------------------------
-- Q5. Profitability ratios — inline calculation
-- ------------------------------------------------------------
SELECT
    f.fiscal_year                                       AS Year,
    ROUND(f.utilidad_neta / NULLIF(f.patrimonio,    0) * 100, 2) AS ROE_Pct,
    ROUND(f.utilidad_neta / NULLIF(f.activos_totales,0) * 100, 2) AS ROA_Pct,
    ROUND(f.ebit / NULLIF(f.activos_totales - f.pasivo_corriente, 0) * 100, 2) AS ROCE_Pct,
    ROUND((f.dias_cxc + f.dias_inventario - f.dias_cxp), 1)      AS CCC_Days
FROM financials f
ORDER BY f.fiscal_year;

-- ------------------------------------------------------------
-- Q6. Power BI flat export — all metrics in one row per year
-- ------------------------------------------------------------
SELECT
    f.fiscal_year                                   AS Year,
    f.ingresos_totales  / 1e6                       AS Revenue_M,
    f.ebitda            / 1e6                       AS EBITDA_M,
    f.utilidad_neta     / 1e6                       AS NetIncome_M,
    f.activos_totales   / 1e6                       AS Assets_M,
    f.patrimonio        / 1e6                       AS Equity_M,
    f.deuda_total       / 1e6                       AS Debt_M,
    ROUND(m.margen_bruto   * 100, 2)                AS GrossMargin_Pct,
    ROUND(m.margen_ebitda  * 100, 2)                AS EBITDAMargin_Pct,
    ROUND(m.margen_neto    * 100, 2)                AS NetMargin_Pct,
    ROUND(r.razon_circulante, 2)                    AS CurrentRatio,
    ROUND(r.deuda_equity,     2)                    AS DE_Ratio,
    ROUND(r.wacc * 100, 2)                          AS WACC_Pct,
    ROUND(f.utilidad_neta / NULLIF(f.patrimonio,0) * 100, 2)      AS ROE_Pct,
    ROUND(f.utilidad_neta / NULLIF(f.activos_totales,0) * 100, 2) AS ROA_Pct
FROM financials f
JOIN margins    m ON m.fiscal_year = f.fiscal_year
JOIN ratios     r ON r.fiscal_year = f.fiscal_year
ORDER BY f.fiscal_year;
GO
