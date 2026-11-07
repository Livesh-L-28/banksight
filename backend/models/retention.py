"""
Operational Retention Entities: RetentionCase, RetentionAction.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from backend.database.connection import Base


class RetentionCase(Base):
    __tablename__ = "retention_cases"

    case_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    rm_id = Column(String(50), ForeignKey("relationship_managers.rm_id"), nullable=True, index=True)
    status = Column(
        String(30),
        default="Identified",
        nullable=False,
        index=True
    )  # Identified, Assigned, Contacted, Offer Proposed, Retained, Not Retained, Closed
    risk_level = Column(String(20), default="High Risk", nullable=False, index=True)
    churn_probability = Column(Float, nullable=False)
    churn_reason = Column(String(200), nullable=True)
    recommended_action = Column(String(200), nullable=True)
    proposed_offer = Column(String(100), nullable=True)
    follow_up_date = Column(Date, nullable=True)
    closed_date = Column(Date, nullable=True)
    outcome_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="retention_cases")
    relationship_manager = relationship("RelationshipManager", back_populates="retention_cases")
    actions = relationship("RetentionAction", back_populates="retention_case", cascade="all, delete-orphan")


class RetentionAction(Base):
    __tablename__ = "retention_actions"

    action_id = Column(String(50), primary_key=True)
    case_id = Column(String(50), ForeignKey("retention_cases.case_id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # Status Change, Note Added, Call Logged, Offer Made
    performed_by = Column(String(100), nullable=False)
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=True)
    notes = Column(Text, nullable=True)
    action_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    retention_case = relationship("RetentionCase", back_populates="actions")
