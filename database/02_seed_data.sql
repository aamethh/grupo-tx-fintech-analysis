-- ============================================================
-- Grupo TX  |  Seed Data  — sourced directly from Excel files
-- ============================================================
USE GrupoTX;
GO

-- ------------------------------------------------------------
-- FINANCIALS  (from 2.xlsx → Tabla Maestra + Ratios sheet)
-- ============================================================
INSERT INTO financials (
    fiscal_year, period_type,
    ingresos_totales, costo_ventas, utilidad_bruta,
    ebitda, ebit, utilidad_neta, gastos_financieros, nopat,
    activos_totales, activo_corriente, pasivo_corriente,
    pasivo_no_corriente, total_pasivos, patrimonio, deuda_total,
    dias_inventario, dias_cxc, dias_cxp
)
VALUES
('2023', 'Annual',
  31436023, 13042200, 18393823,
  11221761, 6406528, 1036253, 10586995, 4804896,
  146854080, 37134132, 37489630,
  35530538, 73020168, 32400000, 114454000,
  40, 55, 23),

('2024', 'Annual',
  38710988, 16060443, 22650545,
  13818715, 11200000, 1276064, 10485288, 8400000,
  148510831, 50456351, 31477334,
  54896554, 86373888, 33499616, 113354464,
  38, 54, 24),

('2025', 'Q2',
  44517636, 17801745, 26715892,
  16559287, 13000000, 1912650, 11359103, 9750000,
  152543200, 52000000, 38000000,
  84801110, 122801110, 29742068, 122801110,
  37, 53, 25);

-- ------------------------------------------------------------
-- MARGINS  (from margenes.xlsx → Hoja1)
-- ------------------------------------------------------------
INSERT INTO margins (fiscal_year, margen_bruto, margen_ebitda, margen_ebit, margen_neto)
VALUES
('2023', 0.5851, 0.3570, 0.2038, 0.0330),
('2024', 0.5851, 0.3650, 0.2893, 0.0330),
('2025', 0.6001, 0.3720, 0.2920, 0.0430);

-- ------------------------------------------------------------
-- RATIOS  (from 2.xlsx → Ratios sheet)
-- ------------------------------------------------------------
INSERT INTO ratios (
    fiscal_year,
    razon_circulante, prueba_acida, capital_trabajo,
    deuda_equity, deuda_activos, pct_deuda, pct_patrimonio,
    cobertura_intereses, wacc
)
VALUES
('2023', 0.9905, 0.8915,   -355498, 4.9961, 0.8332, 0.8332, 0.1668, 0.6051, 0.07615),
('2024', 1.6029, 1.4426, 18979017, 6.2884, 0.8628, 0.8628, 0.1372, 1.0682, 0.07495),
('2025', 1.3684, 1.2316, 14000000, 4.1289, 0.8050, 0.8050, 0.1950, 1.1445, 0.07730);
GO
