-- ============================================================
-- Grupo TX  |  Seed Data  (sample financials 2022-2024)
-- ============================================================
USE GrupoTX;
GO

-- ------------------------------------------------------------
-- Companies
-- ------------------------------------------------------------
INSERT INTO companies (company_code, company_name, sector, country, currency)
VALUES
    ('GTX',  'Grupo TX Financial',    'Fintech',  'Panama', 'USD'),
    ('GFBG', 'Grupo Financiero BG',   'Banking',  'Panama', 'USD'),
    ('BAC',  'BAC Credomatic Panama', 'Banking',  'Panama', 'USD');

-- ------------------------------------------------------------
-- Financials — Grupo TX (GTX)
-- ------------------------------------------------------------
INSERT INTO financials (
    company_id, fiscal_year,
    total_assets, total_liabilities, total_equity,
    gross_loans, investments, total_deposits, aum,
    net_revenue, operating_expenses, net_income,
    interest_income, fee_income,
    npl_ratio, npl_coverage, capital_ratio
)
VALUES
(1, 2022,  850000,  620000,  230000,  410000,  180000,  530000,  620000,
    98000,  38000,  42000,  55000,  28000,  0.0180, 1.5500, 0.2510),

(1, 2023, 1050000,  780000,  270000,  520000,  240000,  680000,  820000,
   128000,  46000,  55000,  72000,  38000,  0.0160, 1.4800, 0.2620),

(1, 2024, 1340000,  990000,  350000,  650000,  310000,  870000, 1100000,
   165000,  56000,  72000,  90000,  52000,  0.0145, 1.3900, 0.2710);

-- ------------------------------------------------------------
-- Financials — GFBG (reference data from prior project)
-- ------------------------------------------------------------
INSERT INTO financials (
    company_id, fiscal_year,
    total_assets, total_liabilities, total_equity,
    gross_loans, investments, total_deposits, aum,
    net_revenue, operating_expenses, net_income,
    interest_income, fee_income,
    npl_ratio, npl_coverage, capital_ratio
)
VALUES
(2, 2023, 18951000, 15527000, 3424000, 11975000, 5125000, 12600000, 14447000,
   2800000,  787000,  692000, 2100000,  560000,  0.0190, 1.5260, 0.2720),

(2, 2024, 19666000, 15969000, 3697000, 12762000, 5350000, 13573000, 16423000,
   3050000,  829000,  798000, 2250000,  640000,  0.0175, 1.3800, 0.2720),

(2, 2025, 21098000, 17029000, 4069000, 13289000, 5970000, 14597000, 19854000,
   3280000,  853000,  845000, 2380000,  740000,  0.0162, 1.2430, 0.2720);

-- ------------------------------------------------------------
-- Time Series — GTX monthly AUM (Jan 2023 – Dec 2024)
-- ------------------------------------------------------------
INSERT INTO time_series (company_id, period_date, period_type, metric_name, metric_value)
VALUES
(1, '2023-01-01', 'monthly', 'aum',        760000),
(1, '2023-02-01', 'monthly', 'aum',        771000),
(1, '2023-03-01', 'monthly', 'aum',        782000),
(1, '2023-04-01', 'monthly', 'aum',        790000),
(1, '2023-05-01', 'monthly', 'aum',        798000),
(1, '2023-06-01', 'monthly', 'aum',        805000),
(1, '2023-07-01', 'monthly', 'aum',        810000),
(1, '2023-08-01', 'monthly', 'aum',        815000),
(1, '2023-09-01', 'monthly', 'aum',        817000),
(1, '2023-10-01', 'monthly', 'aum',        819000),
(1, '2023-11-01', 'monthly', 'aum',        820000),
(1, '2023-12-01', 'monthly', 'aum',        820000),
(1, '2024-01-01', 'monthly', 'aum',        870000),
(1, '2024-02-01', 'monthly', 'aum',        920000),
(1, '2024-03-01', 'monthly', 'aum',        960000),
(1, '2024-04-01', 'monthly', 'aum',        995000),
(1, '2024-05-01', 'monthly', 'aum',       1020000),
(1, '2024-06-01', 'monthly', 'aum',       1045000),
(1, '2024-07-01', 'monthly', 'aum',       1060000),
(1, '2024-08-01', 'monthly', 'aum',       1070000),
(1, '2024-09-01', 'monthly', 'aum',       1080000),
(1, '2024-10-01', 'monthly', 'aum',       1088000),
(1, '2024-11-01', 'monthly', 'aum',       1094000),
(1, '2024-12-01', 'monthly', 'aum',       1100000);
GO
