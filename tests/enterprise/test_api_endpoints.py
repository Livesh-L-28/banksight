"""
Enterprise REST API Integration & RBAC Security Tests
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_health_and_readiness_endpoints():
    """Validates liveness and readiness probe responses."""
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"


def test_authentication_workflow():
    """Validates OAuth2 JWT credential authentication."""
    # Invalid login
    res_bad = client.post("/api/v1/auth/token", data={"username": "admin", "password": "WrongPassword"})
    assert res_bad.status_code == 401

    # Valid admin login
    res_good = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert res_good.status_code == 200
    token_data = res_good.json()
    assert "access_token" in token_data
    assert token_data["role"] == "Admin"

    # Profile lookup with bearer token
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "admin"


def test_rbac_security_authorization():
    """Validates that unauthorized roles receive 403 Forbidden on protected governance endpoints."""
    # Authenticate as DataAnalyst
    res_analyst = client.post("/api/v1/auth/token", data={"username": "analyst", "password": "Analyst@123"})
    assert res_analyst.status_code == 200
    analyst_token = res_analyst.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    # Data Analyst should NOT be allowed to view immutable compliance audit logs
    res_audit_forbidden = client.get("/api/v1/governance/audit-logs", headers=analyst_headers)
    assert res_audit_forbidden.status_code == 403
    assert "Access denied" in res_audit_forbidden.json()["detail"]

    # Authenticate as ComplianceOfficer
    res_compliance = client.post("/api/v1/auth/token", data={"username": "compliance", "password": "Audit@123"})
    assert res_compliance.status_code == 200
    comp_token = res_compliance.json()["access_token"]
    comp_headers = {"Authorization": f"Bearer {comp_token}"}

    # Compliance Officer CAN access audit logs
    res_audit_ok = client.get("/api/v1/governance/audit-logs", headers=comp_headers)
    assert res_audit_ok.status_code == 200
    assert isinstance(res_audit_ok.json(), list)


def test_executive_kpi_api():
    """Validates executive KPI endpoint with token authentication."""
    res_admin = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = res_admin.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_kpi = client.get("/api/v1/kpi/executive", headers=headers)
    assert res_kpi.status_code == 200
    data = res_kpi.json()
    assert "total_customers" in data
    assert data["total_customers"] > 0
    assert "total_deposits" in data


def test_realtime_churn_prediction_api():
    """Validates real-time machine learning inference scoring endpoint."""
    res_admin = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = res_admin.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "customer_id": "CUST-TEST-01",
        "tenure_months": 24,
        "age": 38,
        "annual_income": 95000.0,
        "current_balance": 450.0,
        "balance_to_income_ratio": 0.005,
        "txn_frequency_12m": 12,
        "total_spend_12m": 3400.0,
        "recency_days": 65,
        "complaints_count": 2,
        "digital_banking_active": False,
        "mobile_banking_active": False,
        "loan_count": 0,
        "credit_card_count": 1
    }

    res_pred = client.post("/api/v1/churn/predict", json=payload, headers=headers)
    assert res_pred.status_code == 200
    pred = res_pred.json()
    assert pred["customer_id"] == "CUST-TEST-01"
    assert pred["churn_probability"] >= 0.50  # Should be elevated due to inactivity & complaints
    assert pred["risk_category"] in ["Medium Risk", "High Risk"]
    assert len(pred["contributing_drivers"]) > 0


def test_retention_funnel_api():
    """Validates retention management analytics endpoint."""
    res_admin = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = res_admin.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_funnel = client.get("/api/v1/retention/funnel", headers=headers)
    assert res_funnel.status_code == 200
    funnel = res_funnel.json()
    assert "total_cases" in funnel
    assert "retained_count" in funnel

