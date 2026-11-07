"""
BankSight MLOps Model Retraining & Champion-Challenger Test Suite
Verifies automated retraining, fair lending DIR verification, and champion promotion.
"""

from fastapi.testclient import TestClient
from backend.api.main import app
from analytics.churn.retrainer import EnterpriseModelRetrainer

client = TestClient(app)


def test_retrainer_execution_and_metrics():
    """Verifies that EnterpriseModelRetrainer runs end-to-end and outputs valid metrics."""
    result = EnterpriseModelRetrainer.retrain_and_evaluate(auto_promote=True)
    assert result["success"] is True
    assert "model_id" in result
    assert "challenger_metrics" in result

    metrics = result["challenger_metrics"]
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert "fair_lending_audit" in result
    assert result["fair_lending_audit"]["compliant"] is True


def test_api_retrain_endpoint():
    """Verifies POST /api/v1/churn/retrain endpoint with JWT authentication."""
    # Authenticate as Admin
    login_resp = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger retraining
    resp = client.post("/api/v1/churn/retrain?auto_promote=false", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "challenger_metrics" in data
    assert data["promoted_to_champion"] is False
