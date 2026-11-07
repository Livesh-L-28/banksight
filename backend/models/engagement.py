"""
Customer Engagement & Servicing Entities: CustomerInteraction, Complaint.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from backend.database.connection import Base


class CustomerInteraction(Base):
    __tablename__ = "customer_interactions"

    interaction_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    interaction_date = Column(DateTime, nullable=False, index=True)
    channel = Column(String(30), nullable=False, index=True)  # Branch, Phone, Mobile App, Web Chat, Email
    interaction_type = Column(String(50), nullable=False)  # Inquiry, Account Service, Dispute, Feedback
    sentiment = Column(String(20), default="Neutral", nullable=False)  # Positive, Neutral, Negative
    summary = Column(Text, nullable=True)
    agent_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="interactions")


class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # Fees, Card Declined, Digital Outage, Customer Service
    priority = Column(String(20), default="Medium", nullable=False, index=True)  # Low, Medium, High, Critical
    status = Column(String(30), default="Open", nullable=False, index=True)  # Open, Investigating, Resolved, Escalated
    resolution_days = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    logged_date = Column(DateTime, nullable=False, index=True)
    resolved_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="complaints")
