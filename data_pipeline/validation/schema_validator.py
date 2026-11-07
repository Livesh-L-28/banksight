"""
BankSight Data Validation & Quality Audit Module
Validates incoming tabular data against banking domain schemas, identifies anomalies,
and logs rejected records with explicit root cause reasons.
"""

from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime


CUSTOMER_REQUIRED_COLUMNS = {
    "customer_id", "first_name", "last_name", "date_of_birth", "age",
    "annual_income", "city", "state", "joining_date", "branch_id"
}

TRANSACTION_REQUIRED_COLUMNS = {
    "transaction_id", "account_id", "customer_id", "branch_id",
    "transaction_date", "transaction_type", "amount", "balance_after", "channel"
}


class SchemaValidator:
    def __init__(self):
        pass

    def validate_customers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict]]:
        """
        Validates customer dataframe.
        Returns: (valid_df, rejected_df, quality_audit_metrics)
        """
        audit_metrics = []
        missing_cols = CUSTOMER_REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValueError(f"Schema violation: Missing required customer columns: {missing_cols}")

        rejection_reasons = []

        for _idx, row in df.iterrows():
            reasons = []
            # Check ID non-null
            if pd.isna(row["customer_id"]) or str(row["customer_id"]).strip() == "":
                reasons.append("Missing or empty customer_id")

            # Check Age boundary
            try:
                age_val = float(row["age"])
                if age_val < 18 or age_val > 115:
                    reasons.append(f"Invalid age: {age_val} (must be between 18 and 115)")
            except (ValueError, TypeError):
                reasons.append("Non-numeric age value")

            # Check Income
            try:
                income_val = float(row["annual_income"])
                if income_val < 0:
                    reasons.append(f"Negative annual_income: {income_val}")
            except (ValueError, TypeError):
                reasons.append("Non-numeric annual_income value")

            # Check date formats
            try:
                datetime.fromisoformat(str(row["joining_date"]).split("T")[0])
            except Exception:
                reasons.append(f"Invalid joining_date format: {row['joining_date']}")

            if reasons:
                rejection_reasons.append("; ".join(reasons))
            else:
                rejection_reasons.append(None)

        df_copy = df.copy()
        df_copy["rejection_reason"] = rejection_reasons

        # Check duplicate customer_id
        duplicate_mask = df_copy.duplicated(subset=["customer_id"], keep=False)
        for idx in df_copy[duplicate_mask].index:
            existing = df_copy.at[idx, "rejection_reason"]
            df_copy.at[idx, "rejection_reason"] = (existing + "; " if existing else "") + "Duplicate customer_id"

        rejected_mask = df_copy["rejection_reason"].notna()
        valid_df = df_copy[~rejected_mask].drop(columns=["rejection_reason"])
        rejected_df = df_copy[rejected_mask]

        audit_metrics.append({
            "check_name": "CustomerSchemaValidation",
            "target_table": "customers",
            "total_evaluated": len(df),
            "failed_count": len(rejected_df),
            "failure_rate_pct": round((len(rejected_df) / max(len(df), 1)) * 100, 2),
            "status": "Passed" if len(rejected_df) == 0 else ("Warning" if len(rejected_df) < len(df) * 0.05 else "Failed")
        })

        return valid_df, rejected_df, audit_metrics

    def validate_transactions(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict]]:
        """
        Validates transaction dataframe.
        Returns: (valid_df, rejected_df, quality_audit_metrics)
        """
        audit_metrics = []
        missing_cols = TRANSACTION_REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValueError(f"Schema violation: Missing required transaction columns: {missing_cols}")

        rejection_reasons = []

        for _idx, row in df.iterrows():
            reasons = []
            if pd.isna(row["transaction_id"]) or str(row["transaction_id"]).strip() == "":
                reasons.append("Missing transaction_id")

            try:
                amt = float(row["amount"])
                if amt <= 0:
                    reasons.append(f"Non-positive transaction amount: {amt}")
            except (ValueError, TypeError):
                reasons.append("Non-numeric transaction amount")

            try:
                bal_after = float(row["balance_after"])
                if bal_after < 0:
                    reasons.append(f"Negative balance_after: {bal_after}")
            except (ValueError, TypeError):
                reasons.append("Non-numeric balance_after")

            if reasons:
                rejection_reasons.append("; ".join(reasons))
            else:
                rejection_reasons.append(None)

        df_copy = df.copy()
        df_copy["rejection_reason"] = rejection_reasons

        # Check duplicate transaction_id
        duplicate_mask = df_copy.duplicated(subset=["transaction_id"], keep=False)
        for idx in df_copy[duplicate_mask].index:
            existing = df_copy.at[idx, "rejection_reason"]
            df_copy.at[idx, "rejection_reason"] = (existing + "; " if existing else "") + "Duplicate transaction_id"

        rejected_mask = df_copy["rejection_reason"].notna()
        valid_df = df_copy[~rejected_mask].drop(columns=["rejection_reason"])
        rejected_df = df_copy[rejected_mask]

        audit_metrics.append({
            "check_name": "TransactionSchemaValidation",
            "target_table": "transactions",
            "total_evaluated": len(df),
            "failed_count": len(rejected_df),
            "failure_rate_pct": round((len(rejected_df) / max(len(df), 1)) * 100, 2),
            "status": "Passed" if len(rejected_df) == 0 else ("Warning" if len(rejected_df) < len(df) * 0.05 else "Failed")
        })

        return valid_df, rejected_df, audit_metrics
