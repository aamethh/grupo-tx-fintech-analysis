"""
export_powerbi.py
-----------------
Builds three flat CSVs for Power BI from the real Excel files.

Outputs:
  dashboard/pbi_summary.csv         — all KPIs in one row per year
  dashboard/pbi_margins.csv         — margin trends
  dashboard/pbi_growth.csv          — YoY growth metrics
"""
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

FINANCIALS_FILE = r"data\grupo_tx_financials.xlsx"
MARGINS_FILE    = r"data\grupo_tx_margenes.xlsx"


def load_base() -> pd.DataFrame:
    pnl = pd.read_excel(FINANCIALS_FILE, sheet_name="Tabla Maestra ", header=1)
    pnl.columns = pnl.columns.str.strip()
    pnl = pnl.dropna(subset=["Año"]).copy()
    pnl["Año"] = pnl["Año"].astype(str).str.strip()

    bal = pd.read_excel(FINANCIALS_FILE, sheet_name="Ratios", header=0)
    bal = bal.rename(columns={bal.columns[0]: "Año"})
    bal["Año"] = bal["Año"].astype(str).str.strip()

    mar = pd.read_excel(MARGINS_FILE, sheet_name="Hoja1", header=1)
    mar.columns = mar.columns.str.strip()
    mar = mar.dropna(subset=["Año"]).copy()
    mar["Año"] = mar["Año"].astype(str).str.strip()

    bal_cols = ["Año", "Activo Corriente", "Pasivo Corriente", "Total Activos",
                "Total Pasivos", "Capital de Trabajo", "Razon circulante",
                "D/E", "Deuda/Activos", "Cobertura de intereses", "WACC"]
    bal_cols = [c for c in bal_cols if c in bal.columns]

    df = pnl.merge(bal[bal_cols], on="Año", how="left") \
            .merge(mar[["Año", "Margen bruto %", "Margen EBITDA %"]], on="Año", how="left")
    df = df.rename(columns={"Año": "Año"})

    for col in df.columns:
        if col != "Año":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("Año").reset_index(drop=True)
    return df


def export_summary(df: pd.DataFrame):
    out = pd.DataFrame()
    out["Year"]                 = df["Año"]
    out["Revenue_USD"]          = df["Ingresos totales"].round(0)
    out["EBITDA_USD"]           = df["EBITDA"].round(0)
    out["EBIT_USD"]             = df["EBIT"].round(0)
    out["NetIncome_USD"]        = df["Utilidad Neta"].round(0)
    out["GrossMargin_Pct"]      = (df["Utilidad bruta"] / df["Ingresos totales"] * 100).round(2)
    out["EBITDAMargin_Pct"]     = (df["EBITDA"] / df["Ingresos totales"] * 100).round(2)
    out["EBITMargin_Pct"]       = (df["EBIT"] / df["Ingresos totales"] * 100).round(2)
    out["NetMargin_Pct"]        = (df["Utilidad Neta"] / df["Ingresos totales"] * 100).round(2)
    out["ROE_Pct"]              = (df["Utilidad Neta"] / df["Patrimonio"] * 100).round(2)
    out["ROA_Pct"]              = (df["Utilidad Neta"] / df["Activos Totales"] * 100).round(2)
    out["CurrentRatio"]         = df["Razon circulante"].round(2)
    out["DE_Ratio"]             = df["D/E"].round(2)
    out["Debt_EBITDA"]          = (df["Deuda Total"] / df["EBITDA"]).round(2)
    out["InterestCoverage"]     = df["Cobertura de intereses"].round(2)
    out["WACC_Pct"]             = (df["WACC"] * 100).round(2)
    out["CCC_Days"]             = (df["Días Inventario"] + df["Días CxC"] - df["DíasCxP"]).round(1)

    path = r"dashboard\pbi_summary.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  Exported -> {path}  ({len(out)} rows)")
    return out


def export_margins(df: pd.DataFrame):
    out = pd.DataFrame()
    out["Year"]             = df["Año"]
    out["Revenue_USD"]      = df["Ingresos totales"].round(0)
    out["COGS_USD"]         = df["Costo de ventas"].round(0)
    out["GrossProfit_USD"]  = df["Utilidad bruta"].round(0)
    out["EBITDA_USD"]       = df["EBITDA"].round(0)
    out["GrossMargin_Pct"]  = (df["Utilidad bruta"] / df["Ingresos totales"] * 100).round(2)
    out["EBITDAMargin_Pct"] = (df["EBITDA"] / df["Ingresos totales"] * 100).round(2)
    out["EBITMargin_Pct"]   = (df["EBIT"] / df["Ingresos totales"] * 100).round(2)
    out["NetMargin_Pct"]    = (df["Utilidad Neta"] / df["Ingresos totales"] * 100).round(2)

    path = r"dashboard\pbi_margins.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  Exported -> {path}  ({len(out)} rows)")
    return out


def export_growth(df: pd.DataFrame):
    out = pd.DataFrame()
    out["Year"]                 = df["Año"]
    out["Revenue_USD"]          = df["Ingresos totales"].round(0)
    out["EBITDA_USD"]           = df["EBITDA"].round(0)
    out["NetIncome_USD"]        = df["Utilidad Neta"].round(0)
    out["Revenue_Growth_Pct"]   = (df["Ingresos totales"].pct_change() * 100).round(2)
    out["EBITDA_Growth_Pct"]    = (df["EBITDA"].pct_change() * 100).round(2)
    out["NetIncome_Growth_Pct"] = (df["Utilidad Neta"].pct_change() * 100).round(2)
    out["EBIT_Growth_Pct"]      = (df["EBIT"].pct_change() * 100).round(2)

    path = r"dashboard\pbi_growth.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  Exported -> {path}  ({len(out)} rows)")
    return out


if __name__ == "__main__":
    print("Loading data from Excel files...")
    df = load_base()
    print(f"  {len(df)} periods loaded: {df['Año'].tolist()}\n")

    print("Exporting Power BI datasets...")
    s = export_summary(df)
    export_margins(df)
    export_growth(df)

    print("\n-- Summary Preview --")
    print(s.to_string(index=False))
    print("\nAll Power BI exports complete.")
