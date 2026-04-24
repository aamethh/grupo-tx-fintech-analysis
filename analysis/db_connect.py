"""
db_connect.py
-------------
Single connection factory for SQL Server.
All other scripts import get_engine() from here.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_SERVER   = os.getenv("DB_SERVER",   "localhost")
DB_NAME     = os.getenv("DB_NAME",     "GrupoTX")
DB_USER     = os.getenv("DB_USER",     "")        
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def get_engine() -> Engine:
    if DB_USER:
        conn_str = (
            f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
        )
    else:
        conn_str = (
            f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}"
            "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        )
    return create_engine(conn_str, fast_executemany=True)


def test_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Connected to {DB_SERVER}/{DB_NAME}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
