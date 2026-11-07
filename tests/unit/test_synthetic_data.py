"""
Unit Tests for Synthetic Banking Data Generator and Referential Integrity
"""

import pytest
import pandas as pd
from pathlib import Path

from scripts.generate_synthetic_data import (
    generate_branches, generate_relationship_managers, generate_account_types,
    generate_products, generate_customers, generate_accounts_and_transactions
)

SYNTHETIC_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "synthetic"


def test_synthetic_data_generation_in_memory():
    branches_df = generate_branches(n_branches=5)
    assert len(branches_df) == 5
    assert "branch_id" in branches_df.columns
    assert branches_df["branch_id"].is_unique

    rms_df = generate_relationship_managers(branches_df, n_rms=10)
    assert len(rms_df) == 10
    assert rms_df["branch_id"].isin(branches_df["branch_id"]).all()

    account_types_df = generate_account_types()
    assert len(account_types_df) >= 4

    products_df = generate_products()
    assert len(products_df) >= 5

    customers_df = generate_customers(branches_df, rms_df, n_customers=50)
    assert len(customers_df) == 50
    assert customers_df["customer_id"].is_unique
    assert customers_df["branch_id"].isin(branches_df["branch_id"]).all()
    assert (customers_df["age"] >= 18).all()
    assert (customers_df["annual_income"] > 0).all()

    accounts_df, txns_df, cp_df = generate_accounts_and_transactions(customers_df, account_types_df, branches_df)
    assert len(accounts_df) >= 50
    assert accounts_df["account_id"].is_unique
    assert accounts_df["customer_id"].isin(customers_df["customer_id"]).all()
    assert txns_df["account_id"].isin(accounts_df["account_id"]).all()
    assert txns_df["customer_id"].isin(customers_df["customer_id"]).all()
    assert (txns_df["amount"] > 0).all()


def test_persisted_synthetic_files_referential_integrity():
    """Validates CSV files in data/synthetic/ have referential integrity."""
    cust_df = pd.read_csv(SYNTHETIC_DIR / "customers.csv")
    acc_df = pd.read_csv(SYNTHETIC_DIR / "accounts.csv")
    txn_df = pd.read_csv(SYNTHETIC_DIR / "transactions.csv")
    branch_df = pd.read_csv(SYNTHETIC_DIR / "branches.csv")

    # Referential checks
    assert acc_df["customer_id"].isin(cust_df["customer_id"]).all()
    assert acc_df["branch_id"].isin(branch_df["branch_id"]).all()
    assert txn_df["account_id"].isin(acc_df["account_id"]).all()
    assert txn_df["customer_id"].isin(cust_df["customer_id"]).all()

    # Balance positivity / reasonable range
    assert (acc_df["current_balance"] >= 0).all()
