"""
BankSight Churn Intelligence Orchestration Service
Coordinates predictive modeling, version registration, batch scoring, and database persistence.
"""

import uuid
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from backend.database.connection import get_db_context
from backend.models import ModelVersion, ChurnPrediction, RetentionCase, RetentionAction
from analytics.churn.pipeline import ChurnPredictionPipeline
from backend.services.segmentation_service import SegmentationService


class ChurnService:
    def __init__(self):
        self.pipeline = ChurnPredictionPipeline()
        self.segmentation_service = SegmentationService()

    def run_training_and_scoring(self, persist: bool = True) -> Dict[str, Any]:
        """
        Executes end-to-end model training, benchmarking, version registration,
        and customer scoring.
        """
        features_df = self.segmentation_service.load_customer_data_for_segmentation()
        benchmark_results = self.pipeline.train_and_benchmark(features_df)
        scored_df = self.pipeline.predict_cohort(features_df)

        if persist:
            self._persist_model_versions(benchmark_results)
            self._persist_predictions(scored_df)
            self._auto_enroll_high_risk_retention_cases(scored_df)

        risk_distribution = scored_df["risk_category"].value_counts().reset_index()
        risk_distribution.columns = ["risk_category", "customer_count"]

        return {
            "benchmark_results": benchmark_results["benchmark_results"],
            "champion_model_name": benchmark_results["champion_model_name"],
            "scored_customers_sample": scored_df.head(50),
            "risk_distribution": risk_distribution.to_dict(orient="records")
        }

    def _persist_model_versions(self, benchmark_data: Dict[str, Any]):
        """Persists trained model metrics and hyperparams to model_versions table."""
        with get_db_context() as session:
            session.execute(text("UPDATE model_versions SET is_champion = 0;"))
            session.commit()

            champion_key = benchmark_data["champion_model_name"]
            run_ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            for model_key, res in benchmark_data["benchmark_results"].items():
                m_id = f"MDL-{model_key.upper()[:3]}-{run_ts}"
                is_champ = (model_key == champion_key)

                model_ver = ModelVersion(
                    model_id=m_id,
                    model_name=res["algorithm"],
                    version_tag=f"v1.0-{model_key}-{run_ts}",
                    algorithm=res["algorithm"],
                    accuracy=res["accuracy"],
                    precision=res["precision"],
                    recall=res["recall"],
                    f1_score=res["f1_score"],
                    roc_auc=res["roc_auc"],
                    hyperparameters={"random_state": 42},
                    feature_importances=res["feature_importances"],
                    is_champion=is_champ,
                    training_date=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                session.add(model_ver)
            session.commit()

    def _persist_predictions(self, scored_df: pd.DataFrame):
        """Persists churn predictions into churn_predictions table."""
        with get_db_context() as session:
            session.execute(text("DELETE FROM churn_predictions;"))
            session.commit()

            # Find champion model ID
            champ = session.query(ModelVersion).filter(ModelVersion.is_champion).first()
            champ_id = champ.model_id if champ else "MDL-GBM-DEFAULT"

            prediction_objects = [
                ChurnPrediction(
                    prediction_id=f"PRED-{r['customer_id']}",
                    customer_id=r["customer_id"],
                    model_id=champ_id,
                    churn_probability=r["churn_probability"],
                    risk_category=r["risk_category"],
                    top_churn_factors=r["top_churn_factors"],
                    recommended_action=r["recommended_action"],
                    predicted_date=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                for _, r in scored_df.iterrows()
            ]
            session.bulk_save_objects(prediction_objects)
            session.commit()

    def _auto_enroll_high_risk_retention_cases(self, scored_df: pd.DataFrame):
        """Automatically enrolls High Risk customers into the retention cases queue."""
        high_risk_cohort = scored_df[scored_df["risk_category"] == "High Risk"]
        with get_db_context() as session:
            existing_case_custs = set(
                row[0] for row in session.execute(text("SELECT customer_id FROM retention_cases")).fetchall()
            )

            cases_to_add = []
            actions_to_add = []

            for _idx, r in high_risk_cohort.iterrows():
                c_id = r["customer_id"]
                if c_id not in existing_case_custs:
                    case_id = f"CASE-{datetime.utcnow().strftime('%Y%m%d%H%M')}-{c_id[-4:]}"
                    reason_str = "; ".join(r["top_churn_factors"]) if isinstance(r["top_churn_factors"], list) else str(r["top_churn_factors"])
                    cases_to_add.append(RetentionCase(
                        case_id=case_id,
                        customer_id=c_id,
                        rm_id=r.get("rm_id", None) if pd.notna(r.get("rm_id", None)) else None,
                        status="Identified",
                        risk_level="High Risk",
                        churn_probability=r["churn_probability"],
                        churn_reason=reason_str,
                        recommended_action=r["recommended_action"],
                        created_at=datetime.utcnow()
                    ))
                    actions_to_add.append(RetentionAction(
                        action_id=f"ACT-INIT-{uuid.uuid4().hex[:10]}",
                        case_id=case_id,
                        action_type="Auto-Enrolled",
                        performed_by="ML Churn Early Warning",
                        previous_status=None,
                        new_status="Identified",
                        notes=f"Enrolled with churn probability {r['churn_probability']:.2%}.",
                        action_timestamp=datetime.utcnow()
                    ))

            if cases_to_add:
                session.bulk_save_objects(cases_to_add)
                session.bulk_save_objects(actions_to_add)
                session.commit()
