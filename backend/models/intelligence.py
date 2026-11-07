"""
Customer Intelligence Entities: CustomerSegment, ChurnPrediction, ModelVersion.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from backend.database.connection import Base


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    segment_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    segment_type = Column(String(50), nullable=False, index=True)  # RFM, KMeans, Demographic, Geographic, Financial
    segment_label = Column(String(50), nullable=False, index=True)
    recency_score = Column(Integer, nullable=True)
    frequency_score = Column(Integer, nullable=True)
    monetary_score = Column(Integer, nullable=True)
    cluster_id = Column(Integer, nullable=True)
    confidence_score = Column(Float, default=1.0, nullable=False)
    computed_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="segment_records")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    model_id = Column(String(50), primary_key=True)
    model_name = Column(String(100), nullable=False)  # LogisticRegression, RandomForest, GradientBoosting
    version_tag = Column(String(50), unique=True, nullable=False)
    algorithm = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    feature_importances = Column(JSON, nullable=True)
    is_champion = Column(Boolean, default=False, nullable=False, index=True)
    training_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    predictions = relationship("ChurnPrediction", back_populates="model_version")


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    prediction_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    model_id = Column(String(50), ForeignKey("model_versions.model_id"), nullable=False, index=True)
    churn_probability = Column(Float, nullable=False, index=True)
    risk_category = Column(String(30), nullable=False, index=True)  # Low Risk, Medium Risk, High Risk
    top_churn_factors = Column(JSON, nullable=True)  # List of primary risk drivers
    recommended_action = Column(String(200), nullable=True)
    predicted_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="churn_predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")

