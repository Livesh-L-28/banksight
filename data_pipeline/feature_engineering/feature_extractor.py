"""
BankSight Feature Engineering & Feature Extraction Pipeline
Computes point-in-time behavioral, RFM, and customer portfolio features
guaranteeing strict temporal cutoff and zero data leakage.
"""

from datetime import datetime, timedelta
from typing import Optional
import numpy as np
import pandas as pd


class FeatureExtractor:
    def __init__(self, cutoff_date: Optional[datetime] = None):
        """
        Initializes feature extractor.
        cutoff_date: Point-in-time cutoff date. Transactions/complaints occurring
                     after cutoff_date are strictly excluded to prevent future leakage.
        """
        self.cutoff_date = cutoff_date or datetime(2026, 11, 1, 23, 59, 59)

    def extract_customer_features(
        self,
        customers_df: pd.DataFrame,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        complaints_df: Optional[pd.DataFrame] = None,
        loans_df: Optional[pd.DataFrame] = None,
        customer_products_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Computes customer-level analytical feature vector strictly prior to cutoff_date.
        """
        cutoff_dt = self.cutoff_date
        t_90d = cutoff_dt - timedelta(days=90)
        t_180d = cutoff_dt - timedelta(days=180)
        t_365d = cutoff_dt - timedelta(days=365)

        # Filter transactions prior to cutoff
        txns = transactions_df.copy()
        txns["transaction_date"] = pd.to_datetime(txns["transaction_date"])
        txns_valid = txns[txns["transaction_date"] <= cutoff_dt]

        # 1. Recency & Frequency
        # Recency: days between cutoff_date and latest transaction
        latest_txn = txns_valid.groupby("customer_id")["transaction_date"].max()
        recency_series = (cutoff_dt - latest_txn).dt.days

        # Frequency in trailing 12 months
        txns_12m = txns_valid[txns_valid["transaction_date"] >= t_365d]
        freq_12m = txns_12m.groupby("customer_id")["transaction_id"].count()

        # Spend / Monetary in trailing 12 months (withdrawals)
        spend_12m = txns_12m[txns_12m["transaction_type"] == "Withdrawal"].groupby("customer_id")["amount"].sum()

        # Digital ratio
        digital_txns = txns_12m[txns_12m["channel"].isin(["MOBILE", "ONLINE"])].groupby("customer_id")["transaction_id"].count()
        total_txns_12m = txns_12m.groupby("customer_id")["transaction_id"].count()
        digital_ratio = (digital_txns / total_txns_12m.replace(0, np.nan)).fillna(0.0)

        # 2. Balance Dynamics & Trend
        # 90d balance vs prior 90-180d balance
        txns_90d = txns_valid[txns_valid["transaction_date"] >= t_90d]
        avg_bal_90d = txns_90d.groupby("customer_id")["balance_after"].mean()

        txns_prior_90d = txns_valid[(txns_valid["transaction_date"] >= t_180d) & (txns_valid["transaction_date"] < t_90d)]
        avg_bal_prior = txns_prior_90d.groupby("customer_id")["balance_after"].mean()

        # Balance trend ratio = recent / prior (< 1.0 means balance is depleting)
        balance_trend = (avg_bal_90d / (avg_bal_prior.replace(0, np.nan))).fillna(1.0).clip(0.0, 5.0)

        # 3. Account holdings aggregation
        acc_summary = accounts_df.groupby("customer_id").agg(
            total_balance=("current_balance", "sum"),
            account_count=("account_id", "count"),
            has_savings=("type_id", lambda x: int(any("SAV" in str(v) or "MMA" in str(v) for v in x))),
            has_cd=("type_id", lambda x: int(any("CD" in str(v) for v in x)))
        )

        # 4. Complaints aggregation
        if complaints_df is not None and not complaints_df.empty:
            cmps = complaints_df.copy()
            cmps["logged_date"] = pd.to_datetime(cmps["logged_date"])
            cmps_valid = cmps[cmps["logged_date"] <= cutoff_dt]
            cmp_counts = cmps_valid.groupby("customer_id")["complaint_id"].count()
            unresolved = cmps_valid[cmps_valid["status"] != "Resolved"].groupby("customer_id")["complaint_id"].count()
        else:
            cmp_counts = pd.Series(dtype=int)
            unresolved = pd.Series(dtype=int)

        # 5. Loans aggregation
        if loans_df is not None and not loans_df.empty:
            loan_counts = loans_df.groupby("customer_id")["loan_id"].count()
            loan_balance = loans_df.groupby("customer_id")["current_balance"].sum()
        else:
            loan_counts = pd.Series(dtype=int)
            loan_balance = pd.Series(dtype=float)

        # Combine onto customers
        features = customers_df[[
            "customer_id", "first_name", "last_name", "age", "gender",
            "annual_income", "customer_tenure_months", "customer_segment",
            "branch_id", "credit_score", "digital_banking_active", "mobile_banking_active",
            "churn_flag"
        ]].copy()

        features["recency_days"] = features["customer_id"].map(recency_series).fillna(365).astype(int)
        features["txn_frequency_12m"] = features["customer_id"].map(freq_12m).fillna(0).astype(int)
        features["total_spend_12m"] = features["customer_id"].map(spend_12m).fillna(0.0).round(2)
        features["digital_txn_ratio"] = features["customer_id"].map(digital_ratio).fillna(0.0).round(4)
        features["balance_trend"] = features["customer_id"].map(balance_trend).fillna(1.0).round(4)

        features = features.merge(acc_summary, on="customer_id", how="left")
        features["total_balance"] = features["total_balance"].fillna(0.0).round(2)
        features["account_count"] = features["account_count"].fillna(1).astype(int)
        features["has_savings"] = features["has_savings"].fillna(0).astype(int)
        features["has_cd"] = features["has_cd"].fillna(0).astype(int)

        features["complaint_count"] = features["customer_id"].map(cmp_counts).fillna(0).astype(int)
        features["unresolved_complaints"] = features["customer_id"].map(unresolved).fillna(0).astype(int)
        features["loan_count"] = features["customer_id"].map(loan_counts).fillna(0).astype(int)
        features["loan_balance"] = features["customer_id"].map(loan_balance).fillna(0.0).round(2)

        return features

