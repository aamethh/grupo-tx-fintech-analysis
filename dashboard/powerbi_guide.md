# Power BI Dashboard — Grupo TX

## Data Sources

Connect directly to these CSVs from `/dashboard/`:

| File | Use |
|---|---|
| `financials_flat.csv` | Balance sheet + P&L visuals |
| `metrics_flat.csv` | KPI cards and ratio trends |
| `timeseries_aum.csv` | Monthly AUM line chart |

---

## Recommended Dashboard Structure (3 pages)

---

### Page 1 — Executive Summary

| Visual | Type | Fields |
|---|---|---|
| ROE | KPI Card | `ROE_Pct` (latest year) |
| ROA | KPI Card | `ROA_Pct` |
| AUM Growth | KPI Card | `AUM_Growth_Pct` |
| Capital Ratio | KPI Card | `CapitalRatio` |
| AUM vs Assets vs Loans | Grouped Bar | `AUM_M`, `Assets_M`, `Loans_M` by `Year` |
| Net Income Trend | Line Chart | `NetIncome_M` by `Year` |

---

### Page 2 — Profitability & Efficiency

| Visual | Type | Fields |
|---|---|---|
| ROE Trend | Line Chart | `ROE_Pct` by `Year`, slicer by `Company` |
| ROA Trend | Line Chart | `ROA_Pct` by `Year` |
| Cost-to-Income | Bar Chart | `CostToIncome_Pct` by `Year` |
| Revenue Mix | Stacked Bar | `FeeIncome_M`, `InterestIncome_M` by `Year` |
| Loan-to-Deposit | Line + Ref Line at 90% | `LoanToDeposit_Pct` by `Year` |

---

### Page 3 — AUM & Growth

| Visual | Type | Fields |
|---|---|---|
| Monthly AUM | Line Chart | `AUM_M` by `Period` (from `timeseries_aum.csv`) |
| MoM Growth | Column Chart | `MoM_Growth_Pct` by `Period` |
| AUM Penetration | Gauge / KPI | `AUM_Assets_Pct` vs target 100% |
| Peer Comparison Table | Table | All companies, latest year, sorted by ROE |

---

## Slicers (add to all pages)

- `Company` (multi-select)
- `Year` (range slider)

---

## DAX Measures (add in Power BI)

```dax
ROE YoY Change =
VAR current = SELECTEDVALUE(metrics_flat[ROE_Pct])
VAR prior   = CALCULATE(
    SELECTEDVALUE(metrics_flat[ROE_Pct]),
    FILTER(metrics_flat, metrics_flat[Year] = MAX(metrics_flat[Year]) - 1)
)
RETURN current - prior

AUM CAGR =
VAR first_val = MINX(FILTER(financials_flat, financials_flat[Year] = MIN(financials_flat[Year])), financials_flat[AUM_M])
VAR last_val  = MAXX(FILTER(financials_flat, financials_flat[Year] = MAX(financials_flat[Year])), financials_flat[AUM_M])
VAR n_years   = MAX(financials_flat[Year]) - MIN(financials_flat[Year])
RETURN POWER(DIVIDE(last_val, first_val), DIVIDE(1, n_years)) - 1
```

---

## Color Theme

- Primary:  `#1B3A6B` (Navy)
- Accent:   `#C8972B` (Gold)
- Secondary:`#2E7D9A` (Teal)
- Background: White, grid `#F3F4F6`
