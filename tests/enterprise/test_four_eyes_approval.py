"""
Enterprise Tests for SOX 404 Four-Eyes Principle Dual-Authorization
"""

from fastapi.testclient import TestClient
from backend.api.main import app
from backend.services.retention_service import RetentionService

client = TestClient(app)


def test_four_eyes_threshold_and_approval_workflow():
    """
    Validates:
    1. Low-value concessions ($150) bypass dual-approval and move directly to Offer Proposed.
    2. High-value concessions ($850) are held in 'Pending Approval'.
    3. Submitting RM cannot approve their own concession (Segregation of Duties).
    4. Branch Manager or Executive approves the concession.
    """
    service = RetentionService()
    # Create test retention case
    case_id = service.create_retention_case(
        customer_id="CUST-00001",
        churn_probability=0.75,
        risk_level="High Risk",
        churn_reason="Rate shopping with competitor"
    )

    # Obtain RM token (rm_alex)
    res_rm = client.post("/api/v1/auth/token", data={"username": "rm_alex", "password": "Alex@123"})
    assert res_rm.status_code == 200
    rm_token = res_rm.json()["access_token"]
    rm_headers = {"Authorization": f"Bearer {rm_token}"}

    # 1. Low-value concession ($200) -> Standard discretion applied
    res_low = client.post(
        f"/api/v1/retention/cases/{case_id}/submit-concession",
        json={"offer_name": "Relationship Courtesy Credit", "financial_concession_value": 200.0, "rate_adjustment_bps": 15},
        headers=rm_headers
    )
    assert res_low.status_code == 200
    assert res_low.json()["status"] == "Offer Proposed"
    assert res_low.json()["requires_approval"] is False

    # 2. High-value concession ($950) -> Held in Pending Approval
    res_high = client.post(
        f"/api/v1/retention/cases/{case_id}/submit-concession",
        json={"offer_name": "Executive Deposit Rate Match", "financial_concession_value": 950.0, "rate_adjustment_bps": 65},
        headers=rm_headers
    )
    assert res_high.status_code == 200
    assert res_high.json()["status"] == "Pending Approval"
    assert res_high.json()["requires_approval"] is True

    # 3. Segregation of Duties: RM (rm_alex) tries to approve their own concession
    res_self_approve = client.post(
        f"/api/v1/retention/cases/{case_id}/review-approval",
        json={"approved": True, "notes": "I approve my own offer"},
        headers=rm_headers
    )
    # Must fail because RM role is not in allowed approvers or segregation of duties violation
    assert res_self_approve.status_code in [400, 403]

    # 4. Supervisor (branch_mgr_1) executes dual authorization
    res_mgr = client.post("/api/v1/auth/token", data={"username": "branch_mgr_1", "password": "Branch@123"})
    assert res_mgr.status_code == 200
    mgr_token = res_mgr.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    res_mgr_approve = client.post(
        f"/api/v1/retention/cases/{case_id}/review-approval",
        json={"approved": True, "notes": "Executive approved after commercial yield review."},
        headers=mgr_headers
    )
    assert res_mgr_approve.status_code == 200
    assert res_mgr_approve.json()["decision"] == "APPROVED"
    assert res_mgr_approve.json()["new_status"] == "Offer Proposed"
