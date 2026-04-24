# Grupo TX — Financial Analysis Platform

> Full-stack financial analysis: SQL Server · Python · Excel · Power BI · Monte Carlo
> Built on real company data from `grupo_tx_financials.xlsx` and `grupo_tx_margenes.xlsx`

---

## Data Sources

| File | Content |
|---|---|
| `data/grupo_tx_financials.xlsx` | P&L, Balance Sheet, Ratios (2023–2025) |
| `data/grupo_tx_margenes.xlsx` | Gross and EBITDA margins |
| `grupotx.pbix` | Power BI dashboard (connect to `/dashboard/*.csv`) |
| `Informe Ameth Espinosa.docx` | Narrative financial report |

---

## Key Metrics (real data)

| Metric | 2023 | 2024 | 2025 |
|---|---|---|---|
| Revenue | $31.4M | $38.7M | $44.5M |
| EBITDA Margin | 35.7% | 35.7% | 37.2% |
| Gross Margin | 58.5% | 58.5% | 60.0% |
| Net Margin | 3.3% | 3.3% | 4.3% |
| Revenue Growth | — | +23.1% | +15.0% |
| D/E Ratio | 5.0x | 6.3x | 4.1x |
| CCC (days) | 72 | 68 | 65 |

> **Note:** Total Assets discrepancy between sheets ($146.9M in Tabla Maestra vs $87.6M in Ratios).
> Likely difference in consolidation scope. Use Tabla Maestra as primary source.

---

## Stack

| Layer | Tool | Purpose |
|---|---|---|
| Storage | SQL Server | Structured schema, normalized tables |
| Analysis | Python | Ratio engine, exports, Monte Carlo |
| Executive Output | Excel | Multi-sheet formatted workbook |
| Dashboard | Power BI | Connect to `/dashboard/*.csv` |
| Risk Model | Monte Carlo | AUM/income scenario simulation |

---

## Repository Structure

```
grupo-tx-financials/
├── data/
│   ├── grupo_tx_financials.xlsx    # Source: P&L + Balance + Ratios
│   └── grupo_tx_margenes.xlsx      # Source: Margin analysis
├── database/
│   ├── 01_schema.sql               # Table definitions (5 tables)
│   ├── 02_seed_data.sql            # Pre-populated from Excel
│   └── 03_queries.sql              # 6 analysis queries
├── analysis/
│   ├── db_connect.py               # SQL Server connection factory
│   ├── ingest.py                   # Excel -> SQL Server
│   ├── ratios.py                   # Calculate all metrics (runs without SQL)
│   ├── export_powerbi.py           # Build 3 CSVs for Power BI
│   └── export_excel.py             # Build formatted Excel workbook
├── model/
│   └── scenario_model.py           # Monte Carlo (10k simulations)
├── dashboard/
│   ├── pbi_summary.csv             # All KPIs — connect to Power BI
│   ├── pbi_margins.csv             # Margin trends
│   ├── pbi_growth.csv              # YoY growth metrics
│   └── powerbi_guide.md            # Dashboard structure + DAX measures
└── outputs/
    ├── grupo_tx_metrics.csv        # Full ratio output
    ├── scenario_results.csv        # Monte Carlo P10/P50/P90
    └── scenario_chart.png          # Fan chart
```

---

## How to Run (no SQL Server required)

```bash
pip install pandas openpyxl matplotlib numpy

# Calculate all ratios from Excel
python analysis/ratios.py

# Export CSVs for Power BI
python analysis/export_powerbi.py

# Run Monte Carlo simulation
python model/scenario_model.py
```

## How to Run (with SQL Server)

```bash
pip install sqlalchemy pyodbc

# Set connection (Windows Auth default)
export DB_SERVER=localhost

# Load Excel -> SQL Server
python analysis/ingest.py

# Export from SQL -> Power BI CSVs
python analysis/export_powerbi.py
```

## Power BI Connection

1. Open `grupotx.pbix`
2. Transform Data > Change Source
3. Point each table to the corresponding CSV in `/dashboard/`
4. Refresh — all visuals update automatically

---

## Author

Ameth Espinosa — Financial Analyst Jr.
