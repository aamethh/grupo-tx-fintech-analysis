"""
ingest.py
---------
Loads raw financial data from /data/raw_financials.csv
and writes it to SQL Server via SQLAlchemy.

Run once to populate the database.
"""
import pandas as pd
from sqlalchemy import text
from db_connect import get_engine

RAW_FILE = "data/raw_financials.csv"


def load_raw(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.dropna(subset=["company_id", "fiscal_year"])
    df["fiscal_year"] = df["fiscal_year"].astype(int)
    return df


def get_or_create_company(conn, company_code: str, company_name: str) -> int:
    row = conn.execute(
        text("SELECT company_id FROM companies WHERE company_code = :code"),
        {"code": company_code}
    ).fetchone()
    if row:
        return row[0]
    result = conn.execute(
        text("INSERT INTO companies (company_code, company_name) "
             "OUTPUT INSERTED.company_id VALUES (:code, :name)"),
        {"code": company_code, "name": company_name}
    )
    return result.fetchone()[0]


def upsert_financials(df: pd.DataFrame):
    engine = get_engine()
    numeric_cols = [
        "total_assets", "total_liabilities", "total_equity",
        "gross_loans", "investments", "total_deposits", "aum",
        "net_revenue", "operating_expenses", "net_income",
        "interest_income", "fee_income",
        "npl_ratio", "npl_coverage", "capital_ratio"
    ]
    with engine.begin() as conn:
        for _, row in df.iterrows():
            company_id = get_or_create_company(
                conn, row["company_code"], row.get("company_name", row["company_code"])
            )
            values = {col: row.get(col) for col in numeric_cols}
            values.update({"company_id": company_id, "fiscal_year": int(row["fiscal_year"])})

            existing = conn.execute(
                text("SELECT id FROM financials WHERE company_id=:company_id AND fiscal_year=:fiscal_year"),
                {"company_id": company_id, "fiscal_year": values["fiscal_year"]}
            ).fetchone()

            if existing:
                set_clause = ", ".join([f"{c}=:{c}" for c in numeric_cols])
                conn.execute(
                    text(f"UPDATE financials SET {set_clause} "
                         f"WHERE company_id=:company_id AND fiscal_year=:fiscal_year"),
                    values
                )
                print(f"  Updated: {row['company_code']} {row['fiscal_year']}")
            else:
                cols = ", ".join(["company_id", "fiscal_year"] + numeric_cols)
                params = ", ".join([":company_id", ":fiscal_year"] + [f":{c}" for c in numeric_cols])
                conn.execute(text(f"INSERT INTO financials ({cols}) VALUES ({params})"), values)
                print(f"  Inserted: {row['company_code']} {row['fiscal_year']}")


if __name__ == "__main__":
    print("Loading raw data...")
    df = load_raw(RAW_FILE)
    print(f"  {len(df)} rows loaded from {RAW_FILE}")
    print("Writing to SQL Server...")
    upsert_financials(df)
    print("Done.")
