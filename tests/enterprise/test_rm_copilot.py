"""
Enterprise Tests for Relationship Manager GenAI Copilot
"""

from fastapi.testclient import TestClient
from backend.api.main import app
from backend.copilot.rm_copilot import RMCopilotService

client = TestClient(app)


def test_rm_copilot_service_briefing_generation():
    """Validates heuristic-grounded meeting briefing generation and personalized outreach draft."""
    sample_dossier = {
        "customer_id": "CUST-00042",
        "first_name": "Marcus",
        "last_name": "Brody",
        "full_name": "Marcus Brody",
        "tenure_months": 48,
        "total_balance": 125000.0,
        "churn_probability": 0.65,
        "churn_risk_category": "High Risk",
        "customer_segment": "High Value",
        "occupation": "Surgeon",
        "complaints": [{"subject": "Delayed International Wire", "status": "Closed"}],
        "accounts": [{"account_id": "ACC-001", "account_type": "Savings", "current_balance": 125000.0}]
    }

    briefing = RMCopilotService.generate_meeting_briefing(sample_dossier, actor_name="Alexander Hamilton")

    assert briefing["customer_id"] == "CUST-00042"
    assert "Marcus Brody" in briefing["customer_name"]
    assert "Frustrated" in briefing["sentiment_diagnosis"] or "Yield-Conscious" in briefing["sentiment_diagnosis"]
    assert len(briefing["key_attrition_signals"]) > 0
    assert len(briefing["talking_points_dos"]) > 0
    assert len(briefing["talking_points_donts"]) > 0
    assert "primary_offer" in briefing["recommended_concession_strategy"]
    assert "Subject:" in briefing["email_draft"]
    assert "Alexander Hamilton" in briefing["email_draft"]


def test_rm_copilot_api_endpoint():
    """Validates the authenticated REST API copilot briefing endpoint."""
    # Obtain admin access token
    res_token = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert res_token.status_code == 200
    token = res_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Request briefing for real customer CUST-00001
    res_copilot = client.post("/api/v1/copilot/briefing/CUST-00001", headers=headers)
    assert res_copilot.status_code == 200
    data = res_copilot.json()

    assert data["customer_id"] == "CUST-00001"
    assert "sentiment_diagnosis" in data
    assert "email_draft" in data
    assert len(data["talking_points_dos"]) >= 2

