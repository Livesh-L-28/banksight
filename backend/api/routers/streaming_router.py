"""
BankSight Real-Time Streaming & Attrition Triggers Router
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from backend.api.dependencies import require_roles, log_api_action
from backend.streaming.event_schemas import (
    LargeWithdrawalEvent, ComplaintLoggedEvent, WebhookNotificationPayload
)
from backend.streaming.event_processor import stream_processor
from backend.monitoring.telemetry import capital_flight_alerts_total

router = APIRouter(prefix="/streaming", tags=["Real-Time Streaming & Attrition Triggers"])


@router.post("/events/withdrawal", response_model=Optional[WebhookNotificationPayload])
def process_withdrawal_stream_event(
    event: LargeWithdrawalEvent,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "DataAnalyst"]))
):
    """
    Ingests transaction stream event, analyzes velocity against capital flight rules (>30% drop / >= $25k),
    and dispatches an immediate critical alert if detected.
    """
    alert = stream_processor.process_withdrawal_event(event)
    if alert:
        capital_flight_alerts_total.inc()
        log_api_action(request, user, "TRIGGER_CAPITAL_FLIGHT_ALERT", "STREAM_EVENT", event.event_id)
    return alert


@router.post("/events/complaint", response_model=Optional[WebhookNotificationPayload])
def process_complaint_stream_event(
    event: ComplaintLoggedEvent,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager"]))
):
    """
    Ingests customer service complaint event and escalates critical friction signals.
    """
    alert = stream_processor.process_complaint_event(event)
    if alert:
        log_api_action(request, user, "TRIGGER_COMPLAINT_ESCALATION_ALERT", "STREAM_EVENT", event.event_id)
    return alert


@router.get("/history", response_model=List[Dict[str, Any]])
def get_stream_history(
    limit: int = Query(50, le=200),
    user: dict = Depends(require_roles(["Admin", "Executive", "DataAnalyst"]))
):
    """Returns the recent in-memory streaming event queue."""
    return stream_processor.get_recent_stream_events(limit=limit)


@router.get("/webhooks", response_model=List[Dict[str, Any]])
def get_dispatched_webhooks(
    limit: int = Query(50, le=200),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "ComplianceOfficer"]))
):
    """Returns history of dispatched retention webhook alerts."""
    return stream_processor.get_dispatched_webhooks(limit=limit)

