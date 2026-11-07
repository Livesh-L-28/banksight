"""
Unit Tests for Power BI Semantic Layer Deliverables & Star Schema Datasets
"""

import pytest
import pandas as pd
from pathlib import Path

POWERBI_DIR = Path(__file__).resolve().parent.parent.parent / "powerbi"
DATASETS_DIR = POWERBI_DIR / "datasets"
DAX_FILE = POWERBI_DIR / "dax" / "measures.dax"
EXCEL_MODEL = DATASETS_DIR / "BankSight_PowerBI_Star_Schema.xlsx"


def test_powerbi_star_schema_files_exist():
    expected_files = [
        "DimBranch.csv",
        "DimProduct.csv",
        "DimCustomer.csv",
        "DimAccount.csv",
        "FactTransactions.csv",
        "FactCustomerSnapshot.csv",
        "FactCampaign.csv",
        "FactRetention.csv"
    ]
    for fname in expected_files:
        fpath = DATASETS_DIR / fname
        assert fpath.exists(), f"Missing Power BI star schema file: {fname}"
        assert fpath.stat().st_size > 0, f"Empty Power BI file: {fname}"


def test_star_schema_referential_alignment():
    dim_cust = pd.read_csv(DATASETS_DIR / "DimCustomer.csv")
    fact_txns = pd.read_csv(DATASETS_DIR / "FactTransactions.csv")
    fact_snap = pd.read_csv(DATASETS_DIR / "FactCustomerSnapshot.csv")
    dim_branch = pd.read_csv(DATASETS_DIR / "DimBranch.csv")

    assert fact_txns["CustomerKey"].isin(dim_cust["CustomerKey"]).all()
    assert fact_snap["CustomerKey"].isin(dim_cust["CustomerKey"]).all()
    assert dim_cust["BranchKey"].isin(dim_branch["BranchKey"]).all()


def test_dax_measures_definitions():
    assert DAX_FILE.exists()
    content = DAX_FILE.read_text()

    required_measures = [
        "Total Customers",
        "Active Customers",
        "Customer Churn Rate",
        "Customer Retention Rate",
        "Total Deposits",
        "Average Balance",
        "Campaign Conversion Rate",
        "Average Customer Lifetime Value",
        "Branch Average Deposit",
        "High Risk Customer Count"
    ]
    for measure in required_measures:
        assert measure in content, f"Missing required DAX measure: {measure}"


def test_powerbi_excel_workbook():
    assert EXCEL_MODEL.exists()
    xl = pd.ExcelFile(EXCEL_MODEL)
    sheet_names = xl.sheet_names

    required_sheets = ["DimBranch", "DimProduct", "DimCustomer", "FactTransactions", "FactCustomerSnapshot"]
    for s in required_sheets:
        assert s in sheet_names, f"Missing sheet {s} in Power BI Excel workbook"

