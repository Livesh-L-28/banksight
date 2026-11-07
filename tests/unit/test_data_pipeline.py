"""
Unit Tests for BankSight Data Engineering & Validation Pipeline
"""

import pytest
import pandas as pd
from pathlib import Path

from data_pipeline.ingestion.file_loader import FileLoader
from data_pipeline.validation.schema_validator import SchemaValidator
from data_pipeline.cleaning.cleaner import DataCleaner
from data_pipeline.feature_engineering.feature_extractor import FeatureExtractor


def test_file_loader_validation(tmp_path):
    loader = FileLoader(max_size_bytes=1024)

    # Valid CSV
    valid_csv = tmp_path / "test.csv"
    valid_csv.write_text("col1,col2\n1,2")
    is_valid, msg = loader.validate_file_metadata(valid_csv)
    assert is_valid is True
    assert msg is None

    # Invalid extension
    invalid_ext = tmp_path / "test.exe"
    invalid_ext.write_text("dangerous")
    is_valid, msg = loader.validate_file_metadata(invalid_ext)
    assert is_valid is False
    assert "Invalid file extension" in msg

    # Non-existent
    non_existent = tmp_path / "not_there.csv"
    is_valid, msg = loader.validate_file_metadata(non_existent)
    assert is_valid is False
    assert "File not found" in msg


def test_schema_validator_customers():
    validator = SchemaValidator()

    # Valid customer row
    valid_data = [{
        "customer_id": "CUST-001",
        "first_name": "Alice",
        "last_name": "Smith",
        "date_of_birth": "1990-01-01",
        "age": 34,
        "annual_income": 85000.0,
        "city": "charlotte",
        "state": "nc",
        "joining_date": "2020-05-01",
        "branch_id": "BRN-001"
    }]

    # Invalid customer row: age < 18, negative income
    invalid_data = [{
        "customer_id": "CUST-002",
        "first_name": "Bob",
        "last_name": "Doe",
        "date_of_birth": "2015-01-01",
        "age": 9,
        "annual_income": -5000.0,
        "city": "Atlanta",
        "state": "GA",
        "joining_date": "2021-01-01",
        "branch_id": "BRN-002"
    }]

    df = pd.DataFrame(valid_data + invalid_data)
    valid_df, rejected_df, metrics = validator.validate_customers(df)

    assert len(valid_df) == 1
    assert valid_df.iloc[0]["customer_id"] == "CUST-001"
    assert len(rejected_df) == 1
    assert "Invalid age" in rejected_df.iloc[0]["rejection_reason"]
    assert "Negative annual_income" in rejected_df.iloc[0]["rejection_reason"]
    assert metrics[0]["failed_count"] == 1


def test_data_cleaner():
    cleaner = DataCleaner()
    raw_df = pd.DataFrame([{
        "customer_id": "CUST-001",
        "first_name": "  alice  ",
        "last_name": "smith ",
        "email": "  ALICE.SMITH@TEST.COM ",
        "city": "charlotte",
        "state": "nc",
        "age": "34",
        "annual_income": "85000.556"
    }])

    cleaned = cleaner.clean_customers(raw_df)
    assert cleaned.iloc[0]["first_name"] == "Alice"
    assert cleaned.iloc[0]["last_name"] == "Smith"
    assert cleaned.iloc[0]["email"] == "alice.smith@test.com"
    assert cleaned.iloc[0]["city"] == "Charlotte"
    assert cleaned.iloc[0]["state"] == "NC"
    assert cleaned.iloc[0]["age"] == 34
    assert cleaned.iloc[0]["annual_income"] == 85000.56


def test_feature_extractor():
    from datetime import datetime
    cutoff = datetime(2026, 11, 1)
    extractor = FeatureExtractor(cutoff_date=cutoff)

    cust_df = pd.DataFrame([{
        "customer_id": "CUST-100",
        "first_name": "Test",
        "last_name": "User",
        "age": 40,
        "gender": "Female",
        "annual_income": 90000.0,
        "customer_tenure_months": 24,
        "customer_segment": "Affluent",
        "branch_id": "BRN-001",
        "credit_score": 750,
        "digital_banking_active": True,
        "mobile_banking_active": True,
        "churn_flag": False
    }])

    acc_df = pd.DataFrame([{
        "account_id": "ACC-100",
        "customer_id": "CUST-100",
        "type_id": "TYP-CHK-PRM",
        "current_balance": 12500.0
    }])

    txn_df = pd.DataFrame([
        {
            "transaction_id": "TXN-1",
            "account_id": "ACC-100",
            "customer_id": "CUST-100",
            "branch_id": "BRN-001",
            "transaction_date": "2026-10-15T10:00:00",
            "transaction_type": "Withdrawal",
            "amount": 150.0,
            "balance_after": 12500.0,
            "channel": "MOBILE"
        },
        {
            "transaction_id": "TXN-2",
            "account_id": "ACC-100",
            "customer_id": "CUST-100",
            "branch_id": "BRN-001",
            "transaction_date": "2026-09-01T12:00:00",
            "transaction_type": "Deposit",
            "amount": 3000.0,
            "balance_after": 12650.0,
            "channel": "BRANCH"
        }
    ])

    features = extractor.extract_customer_features(cust_df, acc_df, txn_df)
    assert len(features) == 1
    assert features.iloc[0]["customer_id"] == "CUST-100"
    assert features.iloc[0]["total_balance"] == 12500.0
    assert features.iloc[0]["txn_frequency_12m"] == 2
    assert features.iloc[0]["total_spend_12m"] == 150.0
    assert features.iloc[0]["recency_days"] == (cutoff - datetime(2026, 10, 15, 10, 0, 0)).days
