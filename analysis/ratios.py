"""
ratios.py
---------
Reads financials from Excel (no SQL Server required),
calculates all key fintech metrics, writes metrics table,
and exports CSV for Power BI and Excel.
"""
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

FINANCIALS_FILE = r"data\grupo_tx_financials.xlsx"
MARGINS_FILE    = r"data\grupo_tx_margenes.xlsx"
OUT_CSV         = r"outputs\grupo_tx_metrics.csv"


def load_data() -> pd.DataFrame:
    # P&L from Tabla Maestra (row 1 = header)
    pnl = pd.read_excel(FINANCIALS_FILE, sheet_name="Tabla Maestra ", header=1)
    pnl.columns = pnl.columns.str.strip()
    pnl = pnl.dropna(subset=["Año"]).copy()
    pnl["Año"] = pnl["Año"].astype(str).str.strip()

    # Ratios sheet — header is on row 0 (no extra header row)
    bal = pd.read_excel(FINANCIALS_FILE, sheet_name="Ratios", header=0)
    bal.columns = bal.columns.str.strip() if hasattr(bal.columns[0], 'strip') else bal.columns
    # Rename first column to Año regardless of encoding
    bal = bal.rename(columns={bal.columns[0]: "Año"})
    bal["Año"] = bal["Año"].astype(str).str.strip()

    # Margins
    mar = pd.read_excel(MARGINS_FILE, sheet_name="Hoja1", header=1)
    mar.columns = mar.columns.str.strip()
    mar = mar.dropna(subset=["Año"]).copy()
    mar["Año"] = mar["Año"].astype(str).str.strip()

    bal_cols = ["Año", "Activo Corriente", "Pasivo Corriente", "Total Activos",
                "Total Pasivos", "Capital de Trabajo", "WACC",
                "Razon circulante", "prueba acida", "D/E", "Cobertura de intereses"]
    bal_cols = [c for c in bal_cols if c in bal.columns]

    df = pnl.merge(bal[bal_cols], on="Año", how="left").merge(
        mar[["Año", "Margen bruto %", "Margen EBITDA %"]],
        on="Año", how="left"
    )
    df = df.rename(columns={"Año": "fiscal_year"})
    return df


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d = d.sort_values("fiscal_year").reset_index(drop=True)

    # Ensure numeric
    num = [
        "Ingresos totales", "Costo de ventas", "Utilidad bruta",
        "EBITDA", "EBIT", "Utilidad Neta", "Patrimonio",
        "Activos Totales", "Deuda Total", "Gastos Financieros", "NOPAT",
        "Días Inventario", "Días CxC", "DíasCxP",
        "Activo Corriente", "Pasivo Corriente", "Total Activos", "Total Pasivos",
        "Margen bruto %", "Margen EBITDA %",
        "Razon circulante", "prueba acida", "D/E", "Cobertura de intereses", "WACC"
    ]
    for col in num:
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")

    # ── Profitability ──────────────────────────────────────────
    d["ROE"]  = d["Utilidad Neta"] / d["Patrimonio"]
    d["ROA"]  = d["Utilidad Neta"] / d["Activos Totales"]
    d["ROCE"] = d["EBIT"] / (d["Activos Totales"] - d["Pasivo Corriente"])

    # ── Margins ────────────────────────────────────────────────
    d["Margen_Bruto_Pct"]   = d["Utilidad bruta"] / d["Ingresos totales"]
    d["Margen_EBITDA_Pct"]  = d["EBITDA"]         / d["Ingresos totales"]
    d["Margen_EBIT_Pct"]    = d["EBIT"]            / d["Ingresos totales"]
    d["Margen_Neto_Pct"]    = d["Utilidad Neta"]   / d["Ingresos totales"]

    # ── Growth YoY ─────────────────────────────────────────────
    for col, out in [
        ("Ingresos totales", "Revenue_Growth_YoY"),
        ("EBITDA",           "EBITDA_Growth_YoY"),
        ("Utilidad Neta",    "NetIncome_Growth_YoY"),
        ("Activos Totales",  "Asset_Growth_YoY"),
    ]:
        if col in d.columns:
            d[out] = d[col].pct_change()

    # ── Efficiency ─────────────────────────────────────────────
    if all(c in d.columns for c in ["Días CxC", "Días Inventario", "DíasCxP"]):
        d["CCC"] = d["Días CxC"] + d["Días Inventario"] - d["DíasCxP"]

    # ── Leverage ───────────────────────────────────────────────
    d["Debt_EBITDA"] = d["Deuda Total"] / d["EBITDA"]
    d["Equity_Ratio"] = d["Patrimonio"] / d["Activos Totales"]

    return d


def build_output(d: pd.DataFrame) -> pd.DataFrame:
    pct_cols = [
        "ROE", "ROA", "ROCE",
        "Margen_Bruto_Pct", "Margen_EBITDA_Pct", "Margen_EBIT_Pct", "Margen_Neto_Pct",
        "Revenue_Growth_YoY", "EBITDA_Growth_YoY", "NetIncome_Growth_YoY", "Asset_Growth_YoY",
        "Equity_Ratio"
    ]
    out = d.copy()
    for col in pct_cols:
        if col in out.columns:
            out[col] = (out[col] * 100).round(2)

    for col in ["Debt_EBITDA", "CCC", "Razon circulante", "prueba acida", "D/E",
                "Cobertura de intereses", "WACC"]:
        if col in out.columns:
            out[col] = out[col].round(2)

    display_cols = [
        "fiscal_year",
        "Ingresos totales", "EBITDA", "Utilidad Neta",
        "Margen_Bruto_Pct", "Margen_EBITDA_Pct", "Margen_EBIT_Pct", "Margen_Neto_Pct",
        "Revenue_Growth_YoY", "EBITDA_Growth_YoY", "NetIncome_Growth_YoY",
        "ROE", "ROA", "ROCE",
        "Razon circulante", "D/E", "Debt_EBITDA", "Cobertura de intereses",
        "CCC", "WACC"
    ]
    return out[[c for c in display_cols if c in out.columns]]


if __name__ == "__main__":
    print("Loading data from Excel files...")
    df = load_data()

    print("Calculating ratios...")
    df = calculate(df)

    result = build_output(df)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("\n-- Grupo TX | Key Metrics --\n")
    print(result.to_string(index=False))
    print(f"\nExported -> {OUT_CSV}")
