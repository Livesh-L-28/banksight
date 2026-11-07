"""
Marketing Campaign Entities: Campaign, CampaignAssignment, CampaignResponse.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Date, DateTime, Boolean, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from backend.database.connection import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(String(50), primary_key=True)
    campaign_name = Column(String(100), nullable=False)
    campaign_code = Column(String(30), unique=True, nullable=False)
    objective = Column(String(100), nullable=False)  # Retention, Cross-Sell, Deposit Growth, Reactivation
    target_segment = Column(String(50), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, default=0.0, nullable=False)
    channel = Column(String(30), nullable=False)  # Email, SMS, Mobile Push, Direct Mail, RM Call
    status = Column(String(30), default="Planned", nullable=False, index=True)  # Planned, Active, Completed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assignments = relationship("CampaignAssignment", back_populates="campaign", cascade="all, delete-orphan")


class CampaignAssignment(Base):
    __tablename__ = "campaign_assignments"

    assignment_id = Column(String(50), primary_key=True)
    campaign_id = Column(String(50), ForeignKey("campaigns.campaign_id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    assigned_date = Column(Date, nullable=False)
    contacted = Column(Boolean, default=False, nullable=False)
    contacted_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="assignments")
    customer = relationship("Customer", back_populates="campaign_assignments")
    response = relationship("CampaignResponse", back_populates="assignment", uselist=False, cascade="all, delete-orphan")


class CampaignResponse(Base):
    __tablename__ = "campaign_responses"

    response_id = Column(String(50), primary_key=True)
    assignment_id = Column(String(50), ForeignKey("campaign_assignments.assignment_id"), unique=True, nullable=False, index=True)
    response_date = Column(DateTime, nullable=False)
    responded = Column(Boolean, default=False, nullable=False)
    converted = Column(Boolean, default=False, nullable=False, index=True)
    conversion_date = Column(DateTime, nullable=True)
    attributed_revenue = Column(Float, default=0.0, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assignment = relationship("CampaignAssignment", back_populates="response")
