"""
BankSight Unsupervised K-Means Customer Clustering Engine
Applies standardized feature scaling, configurable cluster optimization, silhouette evaluation,
and empirical business profiling to assign verified descriptive segment labels.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


CLUSTER_FEATURE_COLUMNS = [
    "total_balance",
    "annual_income",
    "txn_frequency_12m",
    "customer_tenure_months",
    "digital_txn_ratio",
    "recency_days"
]


class KMeansSegmenter:
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model: KMeans = None
        self.silhouette: float = 0.0
        self.inertia: float = 0.0
        self.cluster_profiles: pd.DataFrame = None
        self.cluster_label_map: Dict[int, str] = {}

    def fit_predict(self, features_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fits K-Means model on normalized features, calculates silhouette score,
        profiles centroids, and assigns empirical business segment labels.
        """
        df = features_df.copy()

        # Ensure required features exist and are non-null
        for col in CLUSTER_FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = df[col].fillna(0.0)

        X = df[CLUSTER_FEATURE_COLUMNS].values
        X_scaled = self.scaler.fit_transform(X)

        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10
        )
        cluster_labels = self.model.fit_predict(X_scaled)
        df["cluster_id"] = cluster_labels

        self.inertia = float(self.model.inertia_)
        if len(df) > self.n_clusters:
            self.silhouette = float(silhouette_score(X_scaled, cluster_labels))
        else:
            self.silhouette = 0.0

        # Profile clusters to generate empirical business labels
        profiles = df.groupby("cluster_id")[CLUSTER_FEATURE_COLUMNS].mean()
        overall_means = df[CLUSTER_FEATURE_COLUMNS].mean()

        label_map = {}
        for c_id, row in profiles.iterrows():
            bal_ratio = row["total_balance"] / max(overall_means["total_balance"], 1.0)
            inc_ratio = row["annual_income"] / max(overall_means["annual_income"], 1.0)
            dig_ratio = row["digital_txn_ratio"]
            rec_days = row["recency_days"]
            freq = row["txn_frequency_12m"]

            if bal_ratio > 1.8 or inc_ratio > 1.7:
                label_map[c_id] = "Wealth & Affluent Savers"
            elif rec_days > 120 or freq < 3:
                label_map[c_id] = "Dormant Traditionalists"
            elif dig_ratio > 0.70 and freq > overall_means["txn_frequency_12m"]:
                label_map[c_id] = "Active Digital Transactors"
            elif row["customer_tenure_months"] > overall_means["customer_tenure_months"] * 1.3:
                label_map[c_id] = "Loyal Mainstream Core"
            else:
                label_map[c_id] = "Emerging Everyday Retail"

        # Resolve duplicates if any
        used_labels = set()
        for c_id in sorted(label_map.keys()):
            base_label = label_map[c_id]
            if base_label in used_labels:
                label_map[c_id] = f"{base_label} (Cohort {c_id})"
            used_labels.add(label_map[c_id])

        self.cluster_label_map = label_map
        self.cluster_profiles = profiles

        df["kmeans_segment"] = df["cluster_id"].map(label_map)

        evaluation_summary = {
            "n_clusters": self.n_clusters,
            "silhouette_score": round(self.silhouette, 3),
            "inertia": round(self.inertia, 2),
            "cluster_label_mapping": label_map,
            "feature_columns": CLUSTER_FEATURE_COLUMNS
        }

        return df, evaluation_summary

    def get_cluster_profiles_summary(self) -> List[Dict[str, Any]]:
        """Returns structured centroid profile comparison for dashboard display."""
        if self.cluster_profiles is None:
            return []

        summary = []
        for c_id, row in self.cluster_profiles.iterrows():
            summary.append({
                "cluster_id": int(c_id),
                "segment_label": self.cluster_label_map.get(c_id, f"Cluster {c_id}"),
                "avg_balance": round(float(row["total_balance"]), 2),
                "avg_income": round(float(row["annual_income"]), 2),
                "avg_txns_12m": round(float(row["txn_frequency_12m"]), 1),
                "avg_tenure_months": round(float(row["customer_tenure_months"]), 1),
                "digital_adoption_pct": round(float(row["digital_txn_ratio"]) * 100, 1),
                "avg_recency_days": round(float(row["recency_days"]), 1)
            })
        return summary
