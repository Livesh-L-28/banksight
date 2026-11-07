"""
BankSight Enterprise Test Suite: Core Banking Webhooks & Telemetry Exporter
Tests HMAC-SHA256 event signing, subscriber lifecycle, Core Banking dispatch simulator,
and institutional Prometheus SLI/SLO metrics exposition.
"""

import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.monitoring.webhooks import EnterpriseWebhookBus, WebhookEventTypes
from sdk.banksight_client import BankSightClient


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(api_client):
    login_resp = api_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@123"}
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def test_webhook_bus_subscription_lifecycle():
    """Verifies internal subscription management and HMAC-SHA256 signatures."""
    target_url = "https://core-banking.bank.internal/api/v1/events"
    secret_key = "whsec_test_secret_key_8829"

    # 1. Register subscription
    sub = EnterpriseWebhookBus.register_subscription(
        target_url=target_url,
        secret_key=secret_key,
        subscribed_events=[WebhookEventTypes.CAPITAL_FLIGHT, WebhookEventTypes.CHURN_ALERT],
        description="Automated Test Core Hook"
    )
    assert sub["subscription_id"].startswith("WHK-")
    assert sub["target_url"] == target_url
    assert "secret_key" not in sub

    # 2. Verify HMAC signature calculation
    sample_payload = b'{"amount": 50000.0, "customer_id": "CUST-00001"}'
    sig = EnterpriseWebhookBus.generate_signature(sample_payload, secret_key)
    expected_sig = hmac.new(secret_key.encode("utf-8"), sample_payload, hashlib.sha256).hexdigest()
    assert sig == expected_sig

    # 3. Dispatch simulated event
    dispatches = EnterpriseWebhookBus.dispatch_event(
        event_type=WebhookEventTypes.CAPITAL_FLIGHT,
        payload={"customer_id": "CUST-00001", "withdrawal": 60000.0},
        simulate_only=True
    )
    assert len(dispatches) >= 1
    recent = dispatches[0]
    assert recent["delivery_status"] == "SUCCESS"
    assert recent["event_type"] == WebhookEventTypes.CAPITAL_FLIGHT

    # 4. Cleanup subscription
    deleted = EnterpriseWebhookBus.delete_subscription(sub["subscription_id"])
    assert deleted is True


def test_webhook_api_endpoints(api_client, admin_token):
    """Verifies RESTful API endpoints for Webhook management."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create webhook subscription
    create_payload = {
        "target_url": "https://fiserv.bank.internal/hooks/churn",
        "secret_key": "whsec_super_secret_test_2026",
        "subscribed_events": ["CHURN_ALERT", "SOX404_CONCESSION_OVERRIDE"],
        "description": "Fiserv Core Banking Integration Hook"
    }
    resp = api_client.post("/api/v1/webhooks/subscriptions", json=create_payload, headers=headers)
    assert resp.status_code == 201
    created = resp.json()
    sub_id = created["subscription_id"]

    # 2. List webhooks
    list_resp = api_client.get("/api/v1/webhooks/subscriptions", headers=headers)
    assert list_resp.status_code == 200
    subs = list_resp.json()
    assert any(s["subscription_id"] == sub_id for s in subs)

    # 3. Test dispatch event
    dispatch_payload = {
        "event_type": "CHURN_ALERT",
        "sample_payload": {"customer_id": "CUST-00001", "churn_prob": 0.88}
    }
    dispatch_resp = api_client.post("/api/v1/webhooks/test-dispatch", json=dispatch_payload, headers=headers)
    assert dispatch_resp.status_code == 200
    d_data = dispatch_resp.json()
    assert d_data["dispatched_count"] >= 1

    # 4. View deliveries log
    deliv_resp = api_client.get("/api/v1/webhooks/deliveries", headers=headers)
    assert deliv_resp.status_code == 200
    delivs = deliv_resp.json()
    assert len(delivs) > 0

    # 5. Delete webhook subscription
    del_resp = api_client.delete(f"/api/v1/webhooks/subscriptions/{sub_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True


def test_sdk_webhook_methods(api_client, admin_token):
    """Verifies SDK client methods for managing and dispatching webhooks."""
    sdk = BankSightClient(base_url="http://testserver", session=api_client)
    sdk.token = admin_token

    # 1. Register webhook via SDK
    hook = sdk.register_webhook(
        target_url="https://temenos.bank.internal/api/webhook",
        secret_key="temenos_secret_key_123",
        subscribed_events=["CAPITAL_FLIGHT"],
        description="Temenos T24 Ingestion"
    )
    assert "subscription_id" in hook
    hook_id = hook["subscription_id"]

    # 2. List webhooks via SDK
    hooks = sdk.list_webhooks()
    assert len(hooks) > 0

    # 3. Dispatch test webhook via SDK
    dispatch = sdk.dispatch_test_webhook("CAPITAL_FLIGHT")
    assert dispatch["dispatched_count"] >= 1

    # 4. Get deliveries via SDK
    deliveries = sdk.get_webhook_deliveries()
    assert isinstance(deliveries, list)

    # 5. Delete webhook via SDK
    res = sdk.delete_webhook(hook_id)
    assert res["success"] is True


def test_prometheus_institutional_telemetry_metrics(api_client):
    """Verifies that Prometheus metrics endpoint exposes enterprise institutional gauges."""
    resp = api_client.get("/metrics")
    assert resp.status_code == 200
    content = resp.text

    # Standard throughput counters
    assert "banksight_http_requests_total" in content
    assert "banksight_http_request_duration_seconds" in content

    # Enterprise Institutional Gauges
    assert "banksight_portfolio_clv_36m_usd" in content
    assert "banksight_clv_at_risk_usd" in content
    assert "banksight_basel_iii_lcr_pct" in content
    assert "banksight_webhook_deliveries_total" in content

