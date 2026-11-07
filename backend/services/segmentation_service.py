"""
BankSight Customer Segmentation Orchestration Service
Executes RFM, K-Means, Demographic, Geographic, and Financial customer segmentation,
persisting calculated cohorts directly to the database.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from backend.database.connection import get_db_context
from backend.models import CustomerSegment
from data_pipeline.feature_engineering.feature_extractor import FeatureExtractor
from analytics.segmentation.rfm import RFMSegmenter
from analytics.segmentation.kmeans import KMeansSegmenter


class SegmentationService:
    def __init__(self):
        self.rfm_segmenter = RFMSegmenter()
        self.kmeans_segmenter = KMeansSegmenter(n_clusters=5)
        self.feature_extractor = FeatureExtractor()

    def load_customer_data_for_segmentation(self) -> pd.DataFrame:
        """Extracts customer, account, and transaction data from DB into analytical feature matrix."""
        with get_db_context() as session:
            custs_sql = "SELECT * FROM customers"
            accs_sql = "SELECT * FROM accounts"
            txns_sql = "SELECT * FROM transactions WHERE status = 'Completed'"
            cmps_sql = "SELECT * FROM complaints"
            loans_sql = "SELECT * FROM loans"

            custs_df = pd.read_sql(custs_sql, session.bind)
            accs_df = pd.read_sql(accs_sql, session.bind)
            txns_df = pd.read_sql(txns_sql, session.bind)
            cmps_df = pd.read_sql(cmps_sql, session.bind)
            loans_df = pd.read_sql(loans_sql, session.bind)

        features_df = self.feature_extractor.extract_customer_features(
            custs_df, accs_df, txns_df, cmps_df, loans_df
        )
        return features_df

    def run_all_segmentations(self, n_clusters: int = 5, persist: bool = True) -> Dict[str, Any]:
        """
        Runs RFM, K-Means, Demographic, Geographic, and Financial segmentation.
        Optionally persists assignments into customer_segments table.
        """
        features_df = self.load_customer_data_for_segmentation()

        # 1. RFM Segmentation
        rfm_df = self.rfm_segmenter.compute_rfm_scores(features_df)

        # 2. K-Means Clustering
        self.kmeans_segmenter.n_clusters = n_clusters
        segmented_df, kmeans_eval = self.kmeans_segmenter.fit_predict(rfm_df)

        # 3. Demographic Bands
        def demographic_band(row):
            age = row["age"]
            if age < 30:
                return "Gen Z / Young Adult (<30)"
            elif age <= 45:
                return "Prime Working Age (30-45)"
            elif age <= 60:
                return "Mature Established (46-60)"
            else:
                return "Retirement Age (60+)"

        segmented_df["demographic_segment"] = segmented_df.apply(demographic_band, axis=1)

        # 4. Financial Tier
        def financial_tier(row):
            bal = row["total_balance"]
            if bal > 100000:
                return "Private Banking ($100k+)"
            elif bal > 35000:
                return "Premier Affluent ($35k-$100k)"
            elif bal > 10000:
                return "Core Mass ($10k-$35k)"
            else:
                return "Basic Banking (<$10k)"

        segmented_df["financial_segment"] = segmented_df.apply(financial_tier, axis=1)

        # 5. Persist to DB if requested
        if persist:
            self._persist_segments(segmented_df)

        # Distribution Summaries
        rfm_distribution = segmented_df["rfm_segment"].value_counts().reset_index()
        rfm_distribution.columns = ["segment_label", "customer_count"]

        kmeans_distribution = segmented_df["kmeans_segment"].value_counts().reset_index()
        kmeans_distribution.columns = ["segment_label", "customer_count"]

        demographic_distribution = segmented_df["demographic_segment"].value_counts().reset_index()
        demographic_distribution.columns = ["segment_label", "customer_count"]

        financial_distribution = segmented_df["financial_segment"].value_counts().reset_index()
        financial_distribution.columns = ["segment_label", "customer_count"]

        cluster_profiles = self.kmeans_segmenter.get_cluster_profiles_summary()

        return {
            "segmented_dataframe": segmented_df,
            "rfm_distribution": rfm_distribution.to_dict(orient="records"),
            "kmeans_distribution": kmeans_distribution.to_dict(orient="records"),
            "demographic_distribution": demographic_distribution.to_dict(orient="records"),
            "financial_distribution": financial_distribution.to_dict(orient="records"),
            "kmeans_evaluation": kmeans_eval,
            "cluster_profiles": cluster_profiles
        }

    def _persist_segments(self, df: pd.DataFrame):
        """Persists segment assignments into customer_segments table."""
        with get_db_context() as session:
            session.execute(text("DELETE FROM customer_segments;"))
            session.commit()

            segment_objects = []
            for _idx, r in df.iterrows():
                # Persist RFM
                segment_objects.append(CustomerSegment(
                    segment_id=f"SEG-RFM-{r['customer_id']}",
                    customer_id=r["customer_id"],
                    segment_type="RFM",
                    segment_label=r["rfm_segment"],
                    recency_score=int(r["r_score"]),
                    frequency_score=int(r["f_score"]),
                    monetary_score=int(r["m_score"]),
                    cluster_id=None,
                    confidence_score=1.0,
                    computed_date=datetime.utcnow()
                ))
                # Persist KMeans
                segment_objects.append(CustomerSegment(
                    segment_id=f"SEG-KM-{r['customer_id']}",
                    customer_id=r["customer_id"],
                    segment_type="KMeans",
                    segment_label=r["kmeans_segment"],
                    recency_score=None,
                    frequency_score=None,
                    monetary_score=None,
                    cluster_id=int(r["cluster_id"]),
                    confidence_score=0.95,
                    computed_date=datetime.utcnow()
                ))
            session.bulk_save_objects(segment_objects)
            session.commit()
