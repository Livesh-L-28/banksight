"""
BankSight Streaming Event Processor & Attrition Early Warning Engine
Processes streaming ledger events in real time to detect capital flight and service friction.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.streaming.event_schemas import (
    LargeWithdrawalEvent, ComplaintLoggedEvent, WebhookNotificationPayload
)
from backend.database.connection import get_db_context
from backend.models import RetentionCase, Customer, RetentionAction


class StreamingEventProcessor:
    """
    Analyzes transaction and operational stream events, applies velocity rules,
    and dispatches immediate retention alerts and webhooks.
    """

    def __init__(self):
        self._event_history: List[Dict[str, Any]] = []
        self._dispatched_webhooks: List[Dict[str, Any]] = []

    def process_withdrawal_event(self, event: LargeWithdrawalEvent) -> Optional[WebhookNotificationPayload]:
        """
        Analyzes withdrawal event for capital flight signals (> 30% balance drop or > $25,000).
        """
        self._event_history.append({"type": "WITHDRAWAL", "payload": event.model_dump()})
        if len(self._event_history) > 200:
            self._event_history.pop(0)

        # Rule: Run-on-balance trigger (> 30% balance or >= $25k)
        pct_drop = (event.amount / max(event.prior_balance, 1.0)) if event.prior_balance > 0 else 1.0
        is_capital_flight = (event.amount >= 25000.0) or (pct_drop >= 0.30 and event.amount >= 5000.0)

        if not is_capital_flight:
            return None

        # Fetch customer info & auto-open emergency retention case
        customer_name = "Valued Customer"
        branch_id = "BR-001"
        rm_id = None

        with get_db_context() as session:
            customer = session.query(Customer).filter(Customer.customer_id == event.customer_id).first()
            if customer:
                customer_name = f"{customer.first_name} {customer.last_name}"
                branch_id = customer.branch_id
                rm_id = customer.rm_id

            # Check if active case already exists
            existing_case = session.query(RetentionCase).filter(
                RetentionCase.customer_id == event.customer_id,
                RetentionCase.status.in_(["Identified", "Assigned", "Contacted", "Offer Proposed", "Pending Approval"])
            ).first()

            if existing_case:
                existing_case.risk_level = "High Risk"
                existing_case.churn_reason = f"EMERGENCY CAPITAL FLIGHT: ${event.amount:,.2f} withdrawn ({pct_drop:.1%} of balance)"
                action = RetentionAction(
                    action_id=f"ACT-FLT-{uuid.uuid4().hex[:10]}",
                    case_id=existing_case.case_id,
                    action_type="CAPITAL_FLIGHT_STREAM_ALERT",
                    performed_by="Real-Time Event Stream Processor",
                    previous_status=existing_case.status,
                    new_status=existing_case.status,
                    notes=f"Capital flight detected: Large {event.channel} withdrawal of ${event.amount:,.2f}. Escalated to Critical.",
                    action_timestamp=datetime.utcnow()
                )
                session.add(action)
            else:
                new_case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
                new_case = RetentionCase(
                    case_id=new_case_id,
                    customer_id=event.customer_id,
                    rm_id=rm_id,
                    churn_probability=0.88,
                    risk_level="High Risk",
                    status="Assigned" if rm_id else "Identified",
                    churn_reason=f"EMERGENCY CAPITAL FLIGHT: ${event.amount:,.2f} withdrawn ({pct_drop:.1%} of balance)",
                    recommended_action="Immediate same-day RM call to evaluate competitor rate offer and propose retention concession.",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(new_case)
                action = RetentionAction(
                    action_id=f"ACT-FLT-{uuid.uuid4().hex[:10]}",
                    case_id=new_case_id,
                    action_type="CAPITAL_FLIGHT_CASE_OPENED",
                    performed_by="Real-Time Event Stream Processor",
                    previous_status=None,
                    new_status=new_case.status,
                    notes=f"Automated case created: ${event.amount:,.2f} withdrawal ({pct_drop:.1%} balance drop).",
                    action_timestamp=datetime.utcnow()
                )
                session.add(action)
            session.commit()

        # Construct and dispatch webhook alert payload
        webhook = WebhookNotificationPayload(
            webhook_id=f"WH-{uuid.uuid4().hex[:10]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger_type="CAPITAL_FLIGHT_DETECTED",
            severity="Critical",
            customer_id=event.customer_id,
            customer_name=customer_name,
            branch_id=branch_id,
            assigned_rm_id=rm_id,
            alert_title=f"CRITICAL: Capital Flight Detected on {customer_name}",
            summary=f"Large withdrawal of ${event.amount:,.2f} ({pct_drop:.1%} balance drop) processed via {event.channel}.",
            recommended_action="Execute immediate outreach call within 2 hours. Offer high-yield deposit rate match.",
            metadata={"amount": event.amount, "prior_balance": event.prior_balance, "new_balance": event.new_balance}
        )

        self._dispatched_webhooks.append(webhook.model_dump())
        return webhook

    def process_complaint_event(self, event: ComplaintLoggedEvent) -> Optional[WebhookNotificationPayload]:
        """
        Analyzes service complaint stream for multi-complaint escalation.
        """
        self._event_history.append({"type": "COMPLAINT", "payload": event.model_dump()})
        if len(self._event_history) > 200:
            self._event_history.pop(0)

        is_severe = event.severity in ["High", "Critical"]
        if not is_severe:
            return None

        customer_name = "Valued Customer"
        branch_id = "BR-001"
        rm_id = None

        with get_db_context() as session:
            customer = session.query(Customer).filter(Customer.customer_id == event.customer_id).first()
            if customer:
                customer_name = f"{customer.first_name} {customer.last_name}"
                branch_id = customer.branch_id
                rm_id = customer.rm_id

        webhook = WebhookNotificationPayload(
            webhook_id=f"WH-{uuid.uuid4().hex[:10]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger_type="COMPLAINT_ESCALATION",
            severity="High",
            customer_id=event.customer_id,
            customer_name=customer_name,
            branch_id=branch_id,
            assigned_rm_id=rm_id,
            alert_title=f"HIGH: Critical Complaint Logged by {customer_name}",
            summary=f"Service friction in category '{event.category}': {event.subject}",
            recommended_action="RM outreach required to remediate complaint before account closure escalation.",
            metadata={"category": event.category, "severity": event.severity}
        )
        self._dispatched_webhooks.append(webhook.model_dump())
        return webhook

    def get_recent_stream_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns in-memory event stream log."""
        return self._event_history[-limit:]

    def get_dispatched_webhooks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns dispatched webhook history."""
        return self._dispatched_webhooks[-limit:]


# Global streaming processor instance
stream_processor = StreamingEventProcessor()
