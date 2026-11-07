"""
BankSight Data Cleaning & Normalization Engine
Cleanses, normalizes, and harmonizes raw banking data fields.
"""

import pandas as pd


class DataCleaner:
    def clean_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes customer dataset."""
        df_clean = df.copy()

        # Trim text columns
        text_cols = ["first_name", "last_name", "city", "state", "occupation", "address"]
        for col in text_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

        # Standardize state code to uppercase
        if "state" in df_clean.columns:
            df_clean["state"] = df_clean["state"].str.upper()

        # Title-case names & cities
        if "city" in df_clean.columns:
            df_clean["city"] = df_clean["city"].str.title()
        if "first_name" in df_clean.columns:
            df_clean["first_name"] = df_clean["first_name"].str.title()
        if "last_name" in df_clean.columns:
            df_clean["last_name"] = df_clean["last_name"].str.title()

        # Standardize email to lowercase
        if "email" in df_clean.columns:
            df_clean["email"] = df_clean["email"].astype(str).str.strip().str.lower()

        # Cast numerics
        df_clean["age"] = df_clean["age"].astype(int)
        df_clean["annual_income"] = df_clean["annual_income"].astype(float).round(2)

        return df_clean

    def clean_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes transaction dataset."""
        df_clean = df.copy()

        # Standardize channels to uppercase
        if "channel" in df_clean.columns:
            df_clean["channel"] = df_clean["channel"].astype(str).str.strip().str.upper()

        # Standardize types to title case
        if "transaction_type" in df_clean.columns:
            df_clean["transaction_type"] = df_clean["transaction_type"].astype(str).str.strip().str.title()

        # Cast amounts and balances
        df_clean["amount"] = df_clean["amount"].astype(float).round(2)
        df_clean["balance_after"] = df_clean["balance_after"].astype(float).round(2)

        return df_clean
