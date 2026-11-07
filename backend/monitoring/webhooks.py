"""
BankSight Enterprise Real-Time Webhook & Core Banking Event Bus
Dispatches cryptographically signed (HMAC-SHA256) JSON webhooks to Core Banking Systems
(e.g., FIS, Fiserv, Temenos, Finacle, Jack Henry) upon high-risk churn, whale outflows,
SOX 404 four-eyes approvals, model auto-promotions, and Basel III liquidity deficits.
"""

import hmac
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

from backend.monitoring.telemetry import webhook_deliveries_total


WEBHOOK_STORE_PATH = Path("data/webhook_subscriptions.json")
DELIVERY_LOG_PATH = Path("data/webhook_deliveries.json")


class WebhookEventTypes:
    CHURN_ALERT = "CHURN_ALERT"
    CAPITAL_FLIGHT = "CAPITAL_FLIGHT"
    SOX404_CONCESSION_OVERRIDE = "SOX404_CONCESSION_OVERRIDE"
    MODEL_PROMOTION = "MODEL_PROMOTION"
    STRESS_TEST_DEFICIT = "STRESS_TEST_DEFICIT"

    ALL_EVENTS = [
        CHURN_ALERT,
        CAPITAL_FLIGHT,
        SOX404_CONCESSION_OVERRIDE,
        MODEL_PROMOTION,
        STRESS_TEST_DEFICIT
    ]


class EnterpriseWebhookBus:
    """
    Manages webhook subscriptions, cryptographic payload signing,
    and event dispatching with delivery logging and telemetry metrics.
    """

    @classmethod
    def _load_subscriptions(cls) -> List[Dict[str, Any]]:
        if not WEBHOOK_STORE_PATH.exists():
            return []
        try:
            with open(WEBHOOK_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def _save_subscriptions(cls, subs: List[Dict[str, Any]]) -> None:
        WEBHOOK_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(WEBHOOK_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(subs, f, indent=2)

    @classmethod
    def _load_deliveries(cls) -> List[Dict[str, Any]]:
        if not DELIVERY_LOG_PATH.exists():
            return []
        try:
            with open(DELIVERY_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def _record_delivery(cls, record: Dict[str, Any]) -> None:
        deliveries = cls._load_deliveries()
        deliveries.append(record)
        # Keep latest 250 records
        if len(deliveries) > 250:
            deliveries = deliveries[-250:]
        DELIVERY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DELIVERY_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(deliveries, f, indent=2)

    @classmethod
    def register_subscription(
        cls,
        target_url: str,
        secret_key: str,
        subscribed_events: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a new webhook subscriber."""
        events = subscribed_events or WebhookEventTypes.ALL_EVENTS
        # Validate events
        valid_events = [e for e in events if e in WebhookEventTypes.ALL_EVENTS]
        if not valid_events:
            valid_events = WebhookEventTypes.ALL_EVENTS

        sub_id = f"WHK-{uuid.uuid4().hex[:8].upper()}"
        sub_record = {
            "subscription_id": sub_id,
            "target_url": target_url,
            "secret_key": secret_key,
            "subscribed_events": valid_events,
            "description": description or "Core Banking Event Bridge",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "dispatch_count": 0
        }

        subs = cls._load_subscriptions()
        subs.append(sub_record)
        cls._save_subscriptions(subs)
        return {k: v for k, v in sub_record.items() if k != "secret_key"}

    @classmethod
    def list_subscriptions(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        subs = cls._load_subscriptions()
        if active_only:
            subs = [s for s in subs if s.get("is_active", True)]
        # Mask secrets in listing
        return [
            {
                "subscription_id": s["subscription_id"],
                "target_url": s["target_url"],
                "subscribed_events": s.get("subscribed_events", []),
                "description": s.get("description", ""),
                "is_active": s.get("is_active", True),
                "created_at": s.get("created_at"),
                "dispatch_count": s.get("dispatch_count", 0)
            }
            for s in subs
        ]

    @classmethod
    def delete_subscription(cls, subscription_id: str) -> bool:
        subs = cls._load_subscriptions()
        remaining = [s for s in subs if s["subscription_id"] != subscription_id]
        if len(remaining) < len(subs):
            cls._save_subscriptions(remaining)
            return True
        return False

    @classmethod
    def generate_signature(cls, payload_bytes: bytes, secret_key: str) -> str:
        """Computes HMAC-SHA256 hex digest for payload authentication."""
        return hmac.new(
            secret_key.encode("utf-8"),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

    @classmethod
    def dispatch_event(
        cls,
        event_type: str,
        payload: Dict[str, Any],
        simulate_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Dispatches an event payload to all active subscribers registered for event_type.
        If simulate_only is True, does not perform external HTTP request but records synthetic success.
        """
        subs = cls._load_subscriptions()
        target_subs = [
            s for s in subs
            if s.get("is_active", True) and (event_type in s.get("subscribed_events", []))
        ]

        results = []
        event_id = f"EVT-{uuid.uuid4().hex}"
        timestamp = datetime.now(timezone.utc).isoformat()

        envelope = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "platform": "BankSight-Enterprise-v2.0",
            "data": payload
        }
        envelope_bytes = json.dumps(envelope, sort_keys=True).encode("utf-8")

        for s in target_subs:
            secret = s.get("secret_key", "default-key")
            signature = cls.generate_signature(envelope_bytes, secret)
            headers = {
                "Content-Type": "application/json",
                "X-BankSight-Event-ID": event_id,
                "X-BankSight-Event-Type": event_type,
                "X-BankSight-Signature": f"sha256={signature}",
                "X-BankSight-Timestamp": timestamp
            }

            delivery_status = "SUCCESS"
            http_code = 200
            error_message = None

            if not simulate_only:
                try:
                    with httpx.Client(timeout=3.0) as client:
                        resp = client.post(s["target_url"], content=envelope_bytes, headers=headers)
                        http_code = resp.status_code
                        delivery_status = "SUCCESS" if resp.is_success else "FAILED"
                except Exception as exc:
                    delivery_status = "FAILED"
                    http_code = 504
                    error_message = str(exc)

            # Record metrics
            webhook_deliveries_total.labels(event_type=event_type, status=delivery_status).inc()

            delivery_record = {
                "delivery_id": f"DLV-{uuid.uuid4().hex[:8]}",
                "subscription_id": s["subscription_id"],
                "target_url": s["target_url"],
                "event_id": event_id,
                "event_type": event_type,
                "http_status_code": http_code,
                "delivery_status": delivery_status,
                "signature": f"sha256={signature[:12]}...",
                "timestamp": timestamp,
                "error": error_message
            }
            cls._record_delivery(delivery_record)
            results.append(delivery_record)

        return results

    @classmethod
    def get_recent_deliveries(cls, limit: int = 50) -> List[Dict[str, Any]]:
        deliveries = cls._load_deliveries()
        return list(reversed(deliveries))[:limit]

