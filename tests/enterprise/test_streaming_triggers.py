"""
Enterprise Tests for Real-Time Streaming & Attrition Triggers
"""

from fastapi.testclient import TestClient
from backend.api.main import app
from backend.streaming.event_schemas import LargeWithdrawalEvent, ComplaintLoggedEvent
from backend.streaming.event_processor import StreamingEventProcessor

client = TestClient(app)


def test_streaming_processor_capital_flight():
    """Validates velocity rules trigger immediate capital flight webhook alerts."""
    processor = StreamingEventProcessor()

    # Small normal withdrawal -> No alarm
    normal_event = LargeWithdrawalEvent(
        event_id="EVT-TXN-001",
        customer_id="CUST-00001",
        account_id="ACC-00001",
        amount=500.0,
        channel="ATM",
        prior_balance=25000.0,
        new_balance=24500.0
    )
    alert_normal = processor.process_withdrawal_event(normal_event)
    assert alert_normal is None

    # Capital flight withdrawal ($45,000) -> Triggers Critical alert
    flight_event = LargeWithdrawalEvent(
        event_id="EVT-TXN-002",
        customer_id="CUST-00001",
        account_id="ACC-00001",
        amount=45000.0,
        channel="WIRE",
        prior_balance=60000.0,
        new_balance=15000.0
    )
    alert_flight = processor.process_withdrawal_event(flight_event)
    assert alert_flight is not None
    assert alert_flight.trigger_type == "CAPITAL_FLIGHT_DETECTED"
    assert alert_flight.severity == "Critical"
    assert alert_flight.customer_id == "CUST-00001"
    assert len(processor.get_dispatched_webhooks()) == 1


def test_streaming_processor_complaint_escalation():
    """Validates critical service complaints trigger immediate early warning alert."""
    processor = StreamingEventProcessor()

    complaint_event = ComplaintLoggedEvent(
        event_id="EVT-CMP-001",
        customer_id="CUST-00002",
        category="Fee Disputes",
        severity="Critical",
        subject="Unauthorized overdraft fees and delayed check clearance"
    )
    alert = processor.process_complaint_event(complaint_event)
    assert alert is not None
    assert alert.trigger_type == "COMPLAINT_ESCALATION"
    assert alert.severity == "High"


def test_streaming_api_endpoints():
    """Validates authenticated streaming ingestion endpoint."""
    res_admin = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert res_admin.status_code == 200
    token = res_admin.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "event_id": "EVT-STREAM-99",
        "customer_id": "CUST-00003",
        "account_id": "ACC-00003",
        "amount": 35000.0,
        "channel": "WIRE",
        "prior_balance": 50000.0,
        "new_balance": 15000.0
    }

    res_stream = client.post("/api/v1/streaming/events/withdrawal", json=payload, headers=headers)
    assert res_stream.status_code == 200
    alert = res_stream.json()
    assert alert is not None
    assert alert["trigger_type"] == "CAPITAL_FLIGHT_DETECTED"
    assert alert["severity"] == "Critical"

