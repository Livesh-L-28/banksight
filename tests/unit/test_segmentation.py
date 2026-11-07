"""
Unit Tests for Customer Segmentation (RFM & K-Means Clustering)
"""

import pytest
import pandas as pd
import numpy as np

from analytics.segmentation.rfm import RFMSegmenter
from analytics.segmentation.kmeans import KMeansSegmenter
from backend.services.segmentation_service import SegmentationService
from backend.database.connection import get_db_session
from backend.models import CustomerSegment


def test_rfm_segmenter_scoring():
    segmenter = RFMSegmenter()

    # Create dummy customer feature set
    data = []
    for i in range(100):
        data.append({
            "customer_id": f"CUST-{i:03d}",
            "recency_days": (i * 3) % 250 + 5,
            "txn_frequency_12m": (i * 2) % 40 + 1,
            "total_spend_12m": (i * 150.0) % 5000.0 + 100.0,
            "total_balance": (i * 800.0) % 50000.0 + 500.0
        })
    df = pd.DataFrame(data)

    rfm_df = segmenter.compute_rfm_scores(df)

    assert "r_score" in rfm_df.columns
    assert "f_score" in rfm_df.columns
    assert "m_score" in rfm_df.columns
    assert "rfm_segment" in rfm_df.columns
    assert rfm_df["r_score"].between(1, 5).all()
    assert rfm_df["f_score"].between(1, 5).all()
    assert rfm_df["m_score"].between(1, 5).all()

    valid_segments = {
        "High Value", "Loyal Customers", "High Growth Potential",
        "New Customers", "At Risk", "Dormant", "Potential Loyalists", "Low Engagement"
    }
    assert set(rfm_df["rfm_segment"].unique()).issubset(valid_segments)


def test_kmeans_segmenter_execution():
    segmenter = KMeansSegmenter(n_clusters=4, random_state=42)

    data = []
    for i in range(120):
        data.append({
            "customer_id": f"CUST-{i:03d}",
            "total_balance": float(np.random.exponential(15000) + 1000),
            "annual_income": float(np.random.normal(85000, 25000)),
            "txn_frequency_12m": int(np.random.poisson(12) + 1),
            "customer_tenure_months": int(np.random.uniform(6, 60)),
            "digital_txn_ratio": float(np.random.uniform(0.1, 0.95)),
            "recency_days": int(np.random.uniform(2, 180))
        })
    df = pd.DataFrame(data)

    clustered_df, eval_summary = segmenter.fit_predict(df)

    assert "cluster_id" in clustered_df.columns
    assert "kmeans_segment" in clustered_df.columns
    assert eval_summary["n_clusters"] == 4
    assert -1.0 <= eval_summary["silhouette_score"] <= 1.0
    assert len(eval_summary["cluster_label_mapping"]) == 4

    # Verify labels are meaningful strings, not merely digits
    for label in clustered_df["kmeans_segment"].unique():
        assert isinstance(label, str)
        assert not label.isdigit()


def test_segmentation_service_end_to_end():
    service = SegmentationService()
    results = service.run_all_segmentations(n_clusters=4, persist=True)

    assert "segmented_dataframe" in results
    assert len(results["segmented_dataframe"]) == 1000
    assert len(results["rfm_distribution"]) > 0
    assert len(results["kmeans_distribution"]) == 4

    # Verify persistence to DB
    session = get_db_session()
    count = session.query(CustomerSegment).count()
    session.close()
    assert count == 2000  # 1000 RFM + 1000 KMeans

