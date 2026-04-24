# Grupo TX — Fintech Financial Analysis

> **Quantitative financial analysis of Grupo TX**, a Panamanian fintech company.
> Built as a full-stack analytical system: Excel → Python → SQL Server → Power BI → Monte Carlo.

---

## Overview

Grupo TX is analyzed through a multi-tool financial workflow designed to replicate
institutional-grade research processes. The project covers three years of actual financial
data (2023–2025), structured ratio analysis, and a forward-looking simulation model
that quantifies revenue risk and upside over a 5-year horizon.

This repository is **portfolio-ready** — every script runs end-to-end against real source files.

---

## Repository Structure

```
grupo-tx-fintech-analysis/
│
├── data/
│   ├── grupo_tx_financials.xlsx     # Source: P&L, Balance Sheet, Ratios (2023–2025)
│   └── grupo_tx_margenes.xlsx       # Source: Gross and EBITDA margin detail
│
├── analysis/
│   ├── db_connect.py                # SQL Server connection factory
│   ├── ingest.py                    # Excel → SQL Server ingestion (upsert)
│   ├── ratios.py                    # Full ratio engine (runs standalone, no SQL)
│   ├── export_powerbi.py            # Builds 3 dashboard-ready CSVs
│   └── export_excel.py              # Formatted multi-sheet Excel workbook
│
├── database/
│   ├── 01_schema.sql                # 5-table schema: financials, margins, ratios, metrics, time_series
│   ├── 02_seed_data.sql             # Pre-populated from real Excel source
│   └── 03_queries.sql               # 6 analytical queries (P&L, margins, growth, Power BI flat)
│
├── model/
│   ├── monte_carlo.py               # Revenue simulation — GBM, 10,000 runs, 5-year horizon
│   └── scenario_model.py            # AUM/income scenario placeholders
│
├── dashboard/
│   ├── pbi_summary.csv              # 17 KPIs per year — connect directly to Power BI
│   ├── pbi_margins.csv              # Full margin breakdown (gross, EBITDA, EBIT, net)
│   ├── pbi_growth.csv               # YoY revenue, EBITDA, net income growth
│   └── powerbi_guide.md             # Dashboard structure, visuals, DAX measures
│
└── outputs/
    ├── mc_paths.png                 # Simulation fan chart (20 paths + percentile bands)
    ├── mc_histogram.png             # Year-5 revenue distribution (P5/P50/P95)
    ├── mc_summary.csv               # Bear / Base / Bull scenario table
    ├── grupo_tx_metrics.csv         # Full ratio output (ROE, ROA, margins, CCC, WACC)
    ├── scenario_results.csv         # AUM Monte Carlo results
    └── scenario_chart.png           # AUM fan chart
```

---

## Methodology

### 1. Data Pipeline

```
Excel (source) → Python (clean + transform) → SQL Server (store) → Power BI (visualize)
```

- Raw financials read from `grupo_tx_financials.xlsx` and `grupo_tx_margenes.xlsx`
- `ingest.py` standardizes column names and upserts rows into SQL Server
- `ratios.py` runs **standalone** (no SQL required) — calculates all metrics directly from Excel
- `export_powerbi.py` produces three flat CSVs consumable by any BI tool

### 2. Monte Carlo Simulation — Geometric Brownian Motion

Revenue paths modeled as:

```
R(t+1) = R(t) × exp(drift + σ × ε)

where:
  drift  = μ - 0.5σ²       (drift-adjusted log-return)
  μ      = mean log-return from historical data
  σ      = historical volatility of log-returns
  ε      ~ N(0, 1)          (standard normal shock)
```

Parameters estimated from historical revenue (2023–2025):

| Parameter | Value |
|---|---|
| Mean log-return (μ) | 17.4% |
| Annual volatility (σ) | 4.8% |
| Implied mean growth | 19.0% |
| Simulations | 10,000 |
| Horizon | 5 years |

---

## Key Findings

### Historical Performance (2023–2025)

| Metric | 2023 | 2024 | 2025 |
|---|---|---|---|
| Revenue | $31.4M | $38.7M | $44.5M |
| EBITDA Margin | 35.7% | 35.7% | 37.2% |
| Gross Margin | 58.5% | 58.5% | 60.0% |
| Net Margin | 3.3% | 3.3% | 4.3% |
| Revenue Growth | — | **+23.1%** | **+15.0%** |
| EBIT Growth | — | +74.8% | +16.1% |
| D/E Ratio | 5.0x | 6.3x | 4.1x |
| CCC (days) | 72 | 68 | 65 |

### Forward Revenue Scenarios (base: $44.5M, 2025)

| Year | Bear (P5) | Median (P50) | Mean | Bull (P95) |
|---|---|---|---|---|
| 2026 | $48.8M | $53.0M | $53.0M | $57.4M |
| 2027 | $56.1M | $63.0M | $63.1M | $70.5M |
| 2028 | $65.1M | $74.8M | $75.0M | $85.7M |
| 2029 | $75.7M | $88.9M | $89.3M | $104.2M |
| **2030** | **$88.3M** | **$105.6M** | **$106.2M** | **$126.3M** |

### Interpretation

- **Revenue expected to ~2.4x by 2030** (mean scenario vs 2025 base)
- **Downside (P5) still implies ~2x growth** — bear case reaches $88.3M vs $44.5M today
- **Low volatility (4.8%)** reflects consistent, predictable revenue expansion to date
- **Asymmetric risk/reward:** upside ($126M) exceeds downside ($88M) by 44 percentage points

---

## Risk Factors

| Risk | Detail |
|---|---|
| **Limited historical data** | Only 2 annual growth observations — model parameters will stabilize with more years |
| **Overestimation of stability** | Low observed volatility may understate true business risk; widen with caution |
| **Data inconsistency** | Total Assets shows $146.9M in `Tabla Maestra` vs $87.6M in `Ratios` sheet — different consolidation scope; `Tabla Maestra` used as primary |
| **Macro concentration** | Business concentrated in Panama — no geographic diversification buffer |

---

## How to Run

### No SQL Server (standalone)

```bash
pip install pandas openpyxl matplotlib numpy

python analysis/ratios.py           # Calculate all financial ratios
python analysis/export_powerbi.py   # Generate Power BI CSVs
python model/monte_carlo.py         # Run 10,000 revenue simulations
```

### With SQL Server

```bash
pip install sqlalchemy pyodbc

python analysis/ingest.py           # Load Excel → SQL Server
python analysis/export_excel.py     # Build formatted Excel workbook
```

### Connect to Power BI

1. Open `dashboard/grupotx.pbix` (if available)
2. Transform Data → Change Source
3. Point each table to `/dashboard/pbi_*.csv`
4. Refresh — all visuals update automatically

---

## Stack

| Tool | Role |
|---|---|
| Python 3.11+ | Data cleaning, ratio engine, simulation, exports |
| pandas / numpy | Data manipulation and statistical modeling |
| matplotlib | Chart generation (all outputs in `/outputs/`) |
| openpyxl | Excel read/write |
| SQL Server | Structured storage, analytical queries |
| Power BI | Dashboard (connects to CSV exports) |
| Git | Version control |

---

## Author

**Ameth Espinosa** — Financial Analyst Jr.
Panama | [github.com/aamethh](https://github.com/aamethh)

---

*This project is for portfolio and educational purposes.*
*All financial data is from internal company sources.*
