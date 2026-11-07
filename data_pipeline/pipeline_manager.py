"""
BankSight Data Pipeline Orchestrator
Coordinates file ingestion, validation, data quality checks, cleansing,
and feature engineering with full audit persistence.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime

from data_pipeline.ingestion.file_loader import FileLoader
from data_pipeline.validation.schema_validator import SchemaValidator
from data_pipeline.cleaning.cleaner import DataCleaner
from data_pipeline.feature_engineering.feature_extractor import FeatureExtractor
from backend.database.connection import get_db_context
from backend.models import DataQualityResult, DataImportJob

EXPORTS_DIR = Path(__file__).resolve().parent.parent / "data" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class PipelineManager:
    def __init__(self):
        self.loader = FileLoader()
        self.validator = SchemaValidator()
        self.cleaner = DataCleaner()
        self.feature_extractor = FeatureExtractor()

    def run_customer_pipeline(self, file_path: Path) -> Dict[str, Any]:
        """Runs end-to-end ingestion and validation pipeline for customers."""
        raw_df = self.loader.load_tabular_data(file_path)
        valid_df, rejected_df, audit_metrics = self.validator.validate_customers(raw_df)

        # Export rejected records if any
        if not rejected_df.empty:
            rejected_export_path = EXPORTS_DIR / "rejected_customers.csv"
            rejected_df.to_csv(rejected_export_path, index=False)

        clean_df = self.cleaner.clean_customers(valid_df)

        # Log audit metrics in database
        self._record_audit_metrics(audit_metrics)

        return {
            "total_records": len(raw_df),
            "valid_records": len(clean_df),
            "rejected_records": len(rejected_df),
            "clean_dataframe": clean_df,
            "audit_metrics": audit_metrics
        }

    def run_transaction_pipeline(self, file_path: Path) -> Dict[str, Any]:
        """Runs end-to-end ingestion and validation pipeline for transactions."""
        raw_df = self.loader.load_tabular_data(file_path)
        valid_df, rejected_df, audit_metrics = self.validator.validate_transactions(raw_df)

        if not rejected_df.empty:
            rejected_export_path = EXPORTS_DIR / "rejected_transactions.csv"
            rejected_df.to_csv(rejected_export_path, index=False)

        clean_df = self.cleaner.clean_transactions(valid_df)
        self._record_audit_metrics(audit_metrics)

        return {
            "total_records": len(raw_df),
            "valid_records": len(clean_df),
            "rejected_records": len(rejected_df),
            "clean_dataframe": clean_df,
            "audit_metrics": audit_metrics
        }

    def extract_features(
        self,
        customers_df: pd.DataFrame,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        complaints_df: Optional[pd.DataFrame] = None,
        loans_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Extracts analytical features for downstream ML and segmentation."""
        return self.feature_extractor.extract_customer_features(
            customers_df, accounts_df, transactions_df, complaints_df, loans_df
        )

    def _record_audit_metrics(self, audit_metrics: list):
        """Persists data quality metrics to database."""
        try:
            with get_db_context() as session:
                for idx, metric in enumerate(audit_metrics):
                    chk_id = f"CHK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{idx}"
                    result = DataQualityResult(
                        check_id=chk_id,
                        check_name=metric["check_name"],
                        target_table=metric["target_table"],
                        total_evaluated=metric["total_evaluated"],
                        failed_count=metric["failed_count"],
                        failure_rate_pct=metric["failure_rate_pct"],
                        status=metric["status"],
                        executed_at=datetime.utcnow()
                    )
                    session.add(result)
                session.commit()
        except Exception as e:
            print(f"[!] Warning: Could not record audit metrics to DB: {e}")
