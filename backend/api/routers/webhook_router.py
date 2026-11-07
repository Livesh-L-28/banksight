"""
BankSight Real-Time Webhook & Core Banking Integration Router
Enables programmatic registration of event webhooks and audit of outbound deliveries.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from backend.api.dependencies import require_roles, log_api_action
from backend.monitoring.webhooks import EnterpriseWebhookBus, WebhookEventTypes

router = APIRouter(prefix="/webhooks", tags=["Core Banking Webhook Integrations"])


class WebhookCreateRequest(BaseModel):
    target_url: str = Field(..., example="https://core-banking.internal.bank.com/api/v1/events/banksight")
    secret_key: str = Field(..., example="whsec_enterprise_secret_key_9941")
    subscribed_events: Optional[List[str]] = Field(
        default=["CHURN_ALERT", "CAPITAL_FLIGHT", "SOX404_CONCESSION_OVERRIDE", "MODEL_PROMOTION", "STRESS_TEST_DEFICIT"],
        example=["CHURN_ALERT", "CAPITAL_FLIGHT"]
    )
    description: Optional[str] = Field("Core Banking Event Ingestion Hook", example="FIS Core Banking Bridge")


class WebhookTestDispatchRequest(BaseModel):
    event_type: str = Field(default="CHURN_ALERT", example="CAPITAL_FLIGHT")
    sample_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        example={"customer_id": "CUST-00001", "withdrawal_amount": 75000.0, "risk_level": "CRITICAL"}
    )


@router.post("/subscriptions", status_code=status.HTTP_201_CREATED)
def create_webhook_subscription(
    req: WebhookCreateRequest,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Registers a new Core Banking system webhook subscription.
    """
    sub = EnterpriseWebhookBus.register_subscription(
        target_url=req.target_url,
        secret_key=req.secret_key,
        subscribed_events=req.subscribed_events,
        description=req.description
    )
    log_api_action(request, user, "CREATE_WEBHOOK_SUBSCRIPTION", "WEBHOOK", sub["subscription_id"])
    return sub


@router.get("/subscriptions")
def list_webhook_subscriptions(
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "ComplianceOfficer"]))
):
    """
    Lists all active webhook endpoints configured for Core Banking event propagation.
    """
    subs = EnterpriseWebhookBus.list_subscriptions()
    log_api_action(request, user, "LIST_WEBHOOK_SUBSCRIPTIONS", "WEBHOOK", "ALL")
    return subs


@router.delete("/subscriptions/{subscription_id}")
def delete_webhook_subscription(
    subscription_id: str,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Deactivates and removes an existing webhook subscription.
    """
    success = EnterpriseWebhookBus.delete_subscription(subscription_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Webhook subscription '{subscription_id}' not found.")
    log_api_action(request, user, "DELETE_WEBHOOK_SUBSCRIPTION", "WEBHOOK", subscription_id)
    return {"success": True, "subscription_id": subscription_id, "message": "Subscription revoked."}


@router.post("/test-dispatch")
def test_dispatch_webhook(
    req: WebhookTestDispatchRequest,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Dispatches a synthetic test event through the webhook bus to verify HMAC-SHA256 signatures and connectivity.
    """
    if req.event_type not in WebhookEventTypes.ALL_EVENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Must be one of: {WebhookEventTypes.ALL_EVENTS}"
        )

    payload = req.sample_payload or {
        "test": True,
        "customer_id": "CUST-00001",
        "timestamp": "2026-11-07T12:00:00Z",
        "description": "Synthetic Core Banking integration connectivity test"
    }

    results = EnterpriseWebhookBus.dispatch_event(
        event_type=req.event_type,
        payload=payload,
        simulate_only=True
    )

    log_api_action(request, user, "TEST_DISPATCH_WEBHOOK", "WEBHOOK", req.event_type)
    return {
        "dispatched_count": len(results),
        "event_type": req.event_type,
        "deliveries": results
    }


@router.get("/deliveries")
def get_webhook_deliveries(
    request: Request,
    limit: int = 50,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Returns recent outbound webhook delivery receipts with HTTP response codes and HMAC signature tags.
    """
    deliveries = EnterpriseWebhookBus.get_recent_deliveries(limit=limit)
    log_api_action(request, user, "VIEW_WEBHOOK_DELIVERIES", "WEBHOOK", f"limit={limit}")
    return deliveries

