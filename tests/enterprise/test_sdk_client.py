"""
BankSight Official Python SDK Client Test Suite
Verifies client authentication, token injection, error mapping, and enterprise workflows.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from sdk.banksight_client import (
    BankSightClient,
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError
)


@pytest.fixture
def sdk_client():
    test_http_client = TestClient(app)
    # Use TestClient as the underlying session
    return BankSightClient(base_url="http://testserver", session=test_http_client)


def test_sdk_health_and_readiness(sdk_client):
    """Verifies unauthenticated health and readiness endpoints."""
    health = sdk_client.get_health()
    assert health["status"] == "healthy"
    assert "BankSight" in health["service"]

    ready = sdk_client.get_ready()
    assert ready["status"] == "ready"


def test_sdk_authentication_and_whoami(sdk_client):
    """Verifies login workflow and profile fetching."""
    login_res = sdk_client.login("admin", "Admin@123")
    assert "access_token" in login_res
    assert sdk_client.token is not None
    assert sdk_client.current_user["role"] == "Admin"

    profile = sdk_client.get_current_user()
    assert profile["username"] == "admin"
    assert profile["role"] == "Admin"


def test_sdk_invalid_login_raises_authentication_error(sdk_client):
    """Verifies that invalid credentials raise AuthenticationError."""
    with pytest.raises(AuthenticationError):
        sdk_client.login("wrong_user", "wrong_pass")


def test_sdk_unauthenticated_request_raises_error(sdk_client):
    """Verifies that accessing protected endpoint without token raises AuthenticationError."""
    sdk_client.token = None
    with pytest.raises(AuthenticationError):
        sdk_client.get_executive_kpis()


def test_sdk_executive_kpis_and_rankings(sdk_client):
    """Verifies fetching executive KPIs and branch rankings via SDK."""
    sdk_client.login("admin", "Admin@123")

    kpis = sdk_client.get_executive_kpis()
    assert "total_customers" in kpis
    assert kpis["total_customers"] > 0

    rankings = sdk_client.get_branch_rankings()
    assert isinstance(rankings, list)
    assert len(rankings) > 0


def test_sdk_churn_prediction_and_dossier(sdk_client):
    """Verifies ML churn prediction and 360 customer dossier."""
    sdk_client.login("admin", "Admin@123")

    # Churn prediction
    pred = sdk_client.predict_churn("CUST-00001")
    assert "churn_probability" in pred
    assert pred["risk_category"] in ["Low Risk", "Medium Risk", "High Risk"]
    assert len(pred["contributing_drivers"]) > 0

    # Customer dossier
    dossier = sdk_client.get_customer_dossier("CUST-00001")
    assert dossier["customer_id"] == "CUST-00001"
    assert "accounts" in dossier


def test_sdk_copilot_briefing(sdk_client):
    """Verifies AI RM copilot briefing generation via SDK."""
    sdk_client.login("admin", "Admin@123")

    briefing = sdk_client.generate_rm_briefing("CUST-00001")
    assert "executive_summary" in briefing
    assert "talking_points_dos" in briefing
    assert "email_draft" in briefing


def test_sdk_streaming_events(sdk_client):
    """Verifies streaming withdrawal and complaint events via SDK."""
    sdk_client.login("admin", "Admin@123")

    # Withdrawal event
    withdrawal_res = sdk_client.stream_withdrawal_event({
        "event_id": "EVT-SDK-001",
        "customer_id": "CUST-00001",
        "account_id": "ACC-0001",
        "amount": 42000.0,
        "prior_balance": 80000.0,
        "new_balance": 38000.0,
        "channel": "Wire Transfer",
        "timestamp": "2026-11-07T14:00:00Z"
    })
    assert withdrawal_res is not None
    assert withdrawal_res["severity"] == "Critical"
    assert withdrawal_res["trigger_type"] == "CAPITAL_FLIGHT_DETECTED"

    # Complaint event
    complaint_res = sdk_client.stream_complaint_event({
        "event_id": "CMP-SDK-001",
        "customer_id": "CUST-00001",
        "category": "Branch Service",
        "severity": "Critical",
        "subject": "Customer threatened legal action over delayed wire transfer."
    })
    assert complaint_res is not None
    assert complaint_res["severity"] == "High"
    assert complaint_res["trigger_type"] == "COMPLAINT_ESCALATION"


def test_sdk_governance_report(sdk_client):
    """Verifies SR 11-7 model governance report fetching."""
    sdk_client.login("admin", "Admin@123")

    gov = sdk_client.get_governance_report()
    assert "framework" in gov
    assert gov["validation_status"] == "APPROVED_FOR_PRODUCTION"
    assert "fairness_audit" in gov
    assert "stability_metrics" in gov


def test_sdk_rbac_enforcement(sdk_client):
    """Verifies that non-admin/RM role is denied access to dual-authorization review."""
    sdk_client.login("analyst", "Analyst@123")

    with pytest.raises(PermissionDeniedError):
        sdk_client.review_concession_approval(
            case_id="CASE-FAKE-001",
            approved=True,
            notes="Unauthorized approval"
        )
