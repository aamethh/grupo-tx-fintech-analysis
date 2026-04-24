"""
ingest.py
---------
Reads the real Excel files and loads data into SQL Server.

Sources:
  data/grupo_tx_financials.xlsx  →  financials + ratios tables
  data/grupo_tx_margenes.xlsx    →  margins table
"""
import pandas as pd
import warnings
from sqlalchemy import text
from db_connect import get_engine

warnings.filterwarnings("ignore", category=UserWarning)

FINANCIALS_FILE = r"data\grupo_tx_financials.xlsx"
MARGINS_FILE    = r"data\grupo_tx_margenes.xlsx"


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_financials() -> pd.DataFrame:
    """Reads 'Tabla Maestra' (wide) and 'Ratios' sheet, merges into one row per year."""

    # P&L + Balance (from Tabla Maestra)
    pnl = pd.read_excel(FINANCIALS_FILE, sheet_name="Tabla Maestra ", header=1)
    pnl.columns = pnl.columns.str.strip()
    pnl = pnl.dropna(subset=["Año"])
    pnl["Año"] = pnl["Año"].astype(str).str.strip()

    col_map_pnl = {
        "Año":                "fiscal_year",
        "Ingresos totales":   "ingresos_totales",
        "Costo de ventas":    "costo_ventas",
        "Utilidad bruta":     "utilidad_bruta",
        "EBITDA":             "ebitda",
        "EBIT":               "ebit",
        "Utilidad Neta":      "utilidad_neta",
        "Patrimonio":         "patrimonio",
        "Activos Totales":    "activos_totales",
        "Deuda Total":        "deuda_total",
        "Gastos Financieros": "gastos_financieros",
        "NOPAT":              "nopat",
        "Días Inventario":    "dias_inventario",
        "Días CxC":           "dias_cxc",
        "DíasCxP":            "dias_cxp",
    }
    pnl = pnl.rename(columns=col_map_pnl)
    pnl = pnl[[c for c in col_map_pnl.values() if c in pnl.columns]]

    # Balance sheet detail (from Ratios sheet)
    bal = pd.read_excel(FINANCIALS_FILE, sheet_name="Ratios", header=1)
    bal.columns = bal.columns.str.strip()
    bal = bal.dropna(subset=["Año"])
    bal["Año"] = bal["Año"].astype(str).str.strip()

    col_map_bal = {
        "Año":                   "fiscal_year",
        "Activo Corriente":      "activo_corriente",
        "Pasivo Corriente":      "pasivo_corriente",
        "Pasivo No Corriente":   "pasivo_no_corriente",
        "Total Activos":         "activos_totales_r",  # keep separate to compare
        "Total Pasivos":         "total_pasivos",
    }
    bal = bal.rename(columns=col_map_bal)
    bal = bal[[c for c in col_map_bal.values() if c in bal.columns]]

    merged = pnl.merge(bal, on="fiscal_year", how="left")
    return merged


def load_margins() -> pd.DataFrame:
    df = pd.read_excel(MARGINS_FILE, sheet_name="Hoja1", header=1)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Año"])
    df["Año"] = df["Año"].astype(str).str.strip()

    col_map = {
        "Año":                   "fiscal_year",
        "Ingresos totales(USD)": "ingresos_totales",
        "Margen bruto %":        "margen_bruto",
        "Margen EBITDA %":       "margen_ebitda",
    }
    df = df.rename(columns=col_map)
    df = df[[c for c in col_map.values() if c in df.columns]]

    # Derive margins not in the file
    raw = pd.read_excel(FINANCIALS_FILE, sheet_name="Analisis Verical-Horizontal ", header=1)
    # margin data is in rows 9-12 of that sheet — extract directly from 2.xlsx Vertical sheet
    return df


def load_ratios() -> pd.DataFrame:
    df = pd.read_excel(FINANCIALS_FILE, sheet_name="Ratios", header=1)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Año"])
    df["Año"] = df["Año"].astype(str).str.strip()

    col_map = {
        "Año":                     "fiscal_year",
        "Razon circulante":        "razon_circulante",
        "prueba acida":            "prueba_acida",
        "D/E":                     "deuda_equity",
        "Deuda/Activos":           "deuda_activos",
        "Capital de Trabajo":      "capital_trabajo",
        "Cobertura de intereses":  "cobertura_intereses",
        "WACC":                    "wacc",
        "% Deuda":                 "pct_deuda",
        "% Patrimonio":            "pct_patrimonio",
    }
    df = df.rename(columns=col_map)
    return df[[c for c in col_map.values() if c in df.columns]]


# ── Writers ───────────────────────────────────────────────────────────────────

def upsert(conn, table: str, df: pd.DataFrame, key: str = "fiscal_year"):
    for _, row in df.iterrows():
        data = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        exists = conn.execute(
            text(f"SELECT id FROM {table} WHERE {key}=:{key}"),
            {key: data[key]}
        ).fetchone()

        cols   = ", ".join(data.keys())
        params = ", ".join([f":{k}" for k in data.keys()])
        set_cl = ", ".join([f"{k}=:{k}" for k in data.keys() if k != key])

        if exists:
            conn.execute(text(f"UPDATE {table} SET {set_cl} WHERE {key}=:{key}"), data)
            print(f"  Updated  [{table}] {key}={data[key]}")
        else:
            conn.execute(text(f"INSERT INTO {table} ({cols}) VALUES ({params})"), data)
            print(f"  Inserted [{table}] {key}={data[key]}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading Excel files...")
    df_fin = load_financials()
    df_mar = load_margins()
    df_rat = load_ratios()

    print(f"  Financials:  {len(df_fin)} rows | cols: {list(df_fin.columns)}")
    print(f"  Margins:     {len(df_mar)} rows | cols: {list(df_mar.columns)}")
    print(f"  Ratios:      {len(df_rat)} rows | cols: {list(df_rat.columns)}")

    print("\nWriting to SQL Server...")
    engine = get_engine()
    with engine.begin() as conn:
        upsert(conn, "financials", df_fin[
            [c for c in df_fin.columns if c in [
                "fiscal_year", "ingresos_totales", "costo_ventas", "utilidad_bruta",
                "ebitda", "ebit", "utilidad_neta", "patrimonio", "activos_totales",
                "deuda_total", "gastos_financieros", "nopat",
                "dias_inventario", "dias_cxc", "dias_cxp",
                "activo_corriente", "pasivo_corriente", "pasivo_no_corriente", "total_pasivos"
            ]]
        ])
        upsert(conn, "margins", df_mar)
        upsert(conn, "ratios", df_rat[[
            c for c in df_rat.columns if c in [
                "fiscal_year", "razon_circulante", "prueba_acida", "capital_trabajo",
                "deuda_equity", "deuda_activos", "cobertura_intereses", "wacc",
                "pct_deuda", "pct_patrimonio"
            ]
        ]])

    print("\nIngestion complete.")
