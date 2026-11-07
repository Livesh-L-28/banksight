"""
Unit Tests for Machine Learning Churn Predictive Pipeline & Calibration
"""

import pytest
import pandas as pd
import numpy as np

from analytics.churn.pipeline import ChurnPredictionPipeline, MODEL_FEATURE_COLUMNS
from backend.services.churn_service import ChurnService
from backend.database.connection import get_db_session
from backend.models import ModelVersion, ChurnPrediction, RetentionCase


@pytest.fixture
def sample_feature_matrix():
    """Generates synthetic features for ML testing."""
    np.random.seed(42)
    n = 200
    data = []
    for i in range(n):
        churn = int(np.random.random() < 0.20)
        data.append({
            "customer_id": f"CUST-{i:04d}",
            "age": int(np.random.normal(40, 10)),
            "annual_income": float(np.random.normal(75000, 20000)),
            "customer_tenure_months": int(np.random.exponential(24) + 6),
            "credit_score": int(np.random.normal(700, 50)),
            "total_balance": float(np.random.exponential(10000) if not churn else np.random.exponential(1500)),
            "account_count": int(np.random.choice([1, 2, 3])),
            "has_savings": 1,
            "has_cd": 0 if churn else int(np.random.random() < 0.3),
            "recency_days": int(np.random.uniform(5, 40) if not churn else np.random.uniform(60, 180)),
            "txn_frequency_12m": int(np.random.poisson(15) if not churn else np.random.poisson(3)),
            "total_spend_12m": float(np.random.uniform(500, 3000)),
            "digital_txn_ratio": float(np.random.uniform(0.4, 0.9) if not churn else np.random.uniform(0.1, 0.4)),
            "balance_trend": float(np.random.uniform(0.85, 1.2) if not churn else np.random.uniform(0.1, 0.5)),
            "complaint_count": int(np.random.poisson(0.2) if not churn else np.random.poisson(1.5)),
            "unresolved_complaints": 1 if (churn and np.random.random() < 0.5) else 0,
            "loan_count": 0,
            "digital_banking_active": 1,
            "mobile_banking_active": 1,
            "churn_flag": churn
        })
    return pd.DataFrame(data)


def test_pipeline_train_and_benchmark(sample_feature_matrix):
    pipeline = ChurnPredictionPipeline(random_state=42)
    benchmark_out = pipeline.train_and_benchmark(sample_feature_matrix)

    assert "benchmark_results" in benchmark_out
    assert "champion_model_name" in benchmark_out
    results = benchmark_out["benchmark_results"]

    for model_name in ["logistic_regression", "random_forest", "gradient_boosting"]:
        assert model_name in results
        m_eval = results[model_name]
        assert 0.0 <= m_eval["accuracy"] <= 1.0
        assert 0.0 <= m_eval["f1_score"] <= 1.0
        assert 0.5 <= m_eval["roc_auc"] <= 1.0
        assert len(m_eval["confusion_matrix"]) == 2
        assert len(m_eval["feature_importances"]) > 0


def test_pipeline_prediction_and_risk_categorization(sample_feature_matrix):
    pipeline = ChurnPredictionPipeline(random_state=42)
    pipeline.train_and_benchmark(sample_feature_matrix)

    scored_df = pipeline.predict_cohort(sample_feature_matrix)

    assert "churn_probability" in scored_df.columns
    assert "risk_category" in scored_df.columns
    assert "top_churn_factors" in scored_df.columns
    assert "recommended_action" in scored_df.columns

    assert scored_df["churn_probability"].between(0.0, 1.0).all()
    assert set(scored_df["risk_category"].unique()).issubset({"Low Risk", "Medium Risk", "High Risk"})

    # Check factors and actions exist
    assert len(scored_df.iloc[0]["top_churn_factors"]) > 0
    assert len(scored_df.iloc[0]["recommended_action"]) > 0


def test_churn_service_end_to_end():
    service = ChurnService()
    results = service.run_training_and_scoring(persist=True)

    assert "benchmark_results" in results
    assert "champion_model_name" in results
    assert len(results["risk_distribution"]) > 0

    session = get_db_session()
    # Verify model versions stored
    model_count = session.query(ModelVersion).count()
    assert model_count >= 3

    # Verify churn predictions stored
    pred_count = session.query(ChurnPrediction).count()
    assert pred_count == 1000

    # Verify high-risk retention cases were auto-enrolled
    case_count = session.query(RetentionCase).count()
    assert case_count > 0
    session.close()
