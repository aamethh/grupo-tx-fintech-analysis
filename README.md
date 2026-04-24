# Grupo TX — Financial Analysis Platform

> Full-stack financial analysis workflow: SQL Server · Python · Excel · Power BI · Monte Carlo

---

## Stack

| Layer | Tool | Purpose |
|---|---|---|
| Storage | SQL Server | Structured schema, ratio calculations, time series |
| Analysis | Python | Data ingestion, ratio engine, exports |
| Executive Output | Excel | Multi-sheet formatted workbook |
| Dashboard | Power BI | Live KPI visuals from CSV exports |
| Risk Model | Monte Carlo (Python) | AUM and income scenario simulation |

---

## Repository Structure

```
grupo-tx-financials/
├── data/                    # Raw input files (CSV)
├── database/
│   ├── 01_schema.sql        # Table definitions
│   ├── 02_seed_data.sql     # Sample data
│   └── 03_queries.sql       # Analysis queries
├── analysis/
│   ├── db_connect.py        # SQL Server connection factory
│   ├── ingest.py            # Load CSV -> SQL Server
│   ├── ratios.py            # Calculate & store all ratios
│   ├── export_powerbi.py    # Export CSVs for Power BI
│   └── export_excel.py      # Build formatted Excel workbook
├── model/
│   └── scenario_model.py    # Monte Carlo (10k simulations)
├── dashboard/
│   └── powerbi_guide.md     # Dashboard structure + DAX measures
└── outputs/                 # All generated files
```

---

## How to Run

### 1. Set up the database

```sql
-- Run in SQL Server Management Studio (in order)
01_schema.sql
02_seed_data.sql
```

### 2. Install Python dependencies

```bash
pip install pandas sqlalchemy pyodbc openpyxl matplotlib numpy
```

### 3. Configure connection (optional — defaults to localhost Windows Auth)

```bash
export DB_SERVER=your_server
export DB_NAME=GrupoTX
```

### 4. Run the pipeline

```bash
python analysis/ingest.py          # load raw data -> SQL
python analysis/ratios.py          # calculate ratios -> metrics table + CSV
python analysis/export_powerbi.py  # export CSVs for Power BI
python analysis/export_excel.py    # build Excel workbook
python model/scenario_model.py     # run Monte Carlo simulation
```

---

## Monte Carlo Output (10,000 simulations, 3-year horizon)

| Year | AUM Bear (P10) | AUM Base (P50) | AUM Bull (P90) |
|---|---|---|---|
| 2025 | $1,235M | $1,320M | $1,405M |
| 2026 | $1,443M | $1,582M | $1,727M |
| 2027 | $1,694M | $1,895M | $2,113M |

---

## Author

Ameth Espinosa — Financial Analyst Jr.
