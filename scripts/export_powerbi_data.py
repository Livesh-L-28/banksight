"""
BankSight Power BI Semantic Layer Data Exporter
Extracts Star Schema Fact & Dimension tables from relational database into
verified CSV and multi-tab Excel workbooks ready for Power BI Desktop.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.connection import get_db_context

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "powerbi" / "datasets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SQL_VIEWS_FILE = Path(__file__).resolve().parent.parent / "powerbi" / "sql_views" / "star_schema_views.sql"


def export_powerbi_star_schema():
    """Extracts and persists Power BI Star Schema tables."""
    print("[*] Initializing Power BI Star Schema Views...")

    with get_db_context() as session:
        # 1. Execute SQL views script
        with open(SQL_VIEWS_FILE, "r") as f:
            sql_statements = f.read().split(";")
            for stmt in sql_statements:
                stmt_clean = stmt.strip()
                if stmt_clean:
                    session.execute(text(stmt_clean))
            session.commit()

        tables_to_export = [
            "DimBranch",
            "DimProduct",
            "DimCustomer",
            "DimAccount",
            "FactTransactions",
            "FactCustomerSnapshot",
            "FactCampaign",
            "FactRetention"
        ]

        excel_path = OUTPUT_DIR / "BankSight_PowerBI_Star_Schema.xlsx"
        print(f"[+] Exporting Star Schema tables to {OUTPUT_DIR} and {excel_path.name}...")

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            for tbl in tables_to_export:
                df = pd.read_sql(f"SELECT * FROM {tbl}", session.bind)
                csv_path = OUTPUT_DIR / f"{tbl}.csv"
                df.to_csv(csv_path, index=False)
                # Write to Excel sheet (truncate transactions sample to 15,000 for excel size sanity if needed)
                excel_df = df.head(15000) if tbl == "FactTransactions" else df
                excel_df.to_excel(writer, sheet_name=tbl, index=False)
                print(f"    - {tbl:24s} : {len(df):6d} rows -> {csv_path.name} ({csv_path.stat().st_size / 1024:.1f} KB)")

    print("[+] Power BI Star Schema export successfully completed!")


if __name__ == "__main__":
    export_powerbi_star_schema()
