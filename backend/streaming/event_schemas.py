"""
BankSight Event-Driven Streaming Message & Alert Schemas
"""

import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class LargeWithdrawalEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:10]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    customer_id: str
    account_id: str
    amount: float
    channel: str = "WIRE"  # WIRE, ACH, ATM, BRANCH
    prior_balance: float
    new_balance: float
    currency: str = "USD"


class ComplaintLoggedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"CMP-EVT-{uuid.uuid4().hex[:10]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    customer_id: str
    category: str
    severity: str  # Low, Medium, High, Critical
    subject: str


class WebhookNotificationPayload(BaseModel):
    webhook_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trigger_type: str  # CAPITAL_FLIGHT_DETECTED, COMPLAINT_ESCALATION, DISENGAGEMENT
    severity: str      # High, Critical
    customer_id: str
    customer_name: str
    branch_id: str
    assigned_rm_id: Optional[str] = None
    alert_title: str
    summary: str
    recommended_action: str
    metadata: Dict[str, Any] = {}

