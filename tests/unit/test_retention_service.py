"""
Unit Tests for Operational Retention Management Workflows & Status Persistence
"""

import pytest
from datetime import date
from backend.services.retention_service import RetentionService
from backend.database.connection import get_db_session
from backend.models import RetentionCase, RetentionAction


def test_retention_case_crud_and_status_transitions():
    service = RetentionService()

    # 1. Create case
    case_id = service.create_retention_case(
        customer_id="CUST-00005",
        churn_probability=0.88,
        risk_level="High Risk",
        churn_reason="Sudden $20,000 balance transfer to competitor",
        recommended_action="Executive RM consultation + APY match",
        follow_up_date=date(2026, 11, 15)
    )
    assert case_id is not None
    assert "CASE-" in case_id

    # 2. Verify initial status
    cases = service.get_cases(status_filter="Identified")
    matching = [c for c in cases if c["case_id"] == case_id]
    assert len(matching) == 1
    assert matching[0]["status"] == "Identified"
    assert matching[0]["churn_probability"] == 0.88

    # 3. Assign RM
    service.assign_relationship_manager(
        case_id=case_id,
        rm_id="RM-001",
        performed_by="Retention Supervisor",
        notes="Assigned to lead wealth officer."
    )
    cases_assigned = service.get_cases(status_filter="Assigned")
    matching_assigned = [c for c in cases_assigned if c["case_id"] == case_id]
    assert len(matching_assigned) == 1
    assert matching_assigned[0]["status"] == "Assigned"
    assert matching_assigned[0]["rm_id"] == "RM-001"

    # 4. Progress status to Contacted
    service.update_case(
        case_id=case_id,
        new_status="Contacted",
        performed_by="RM Sarah",
        notes="Called customer; discussed savings yield options."
    )

    # 5. Progress to Offer Proposed
    service.update_case(
        case_id=case_id,
        new_status="Offer Proposed",
        performed_by="RM Sarah",
        notes="Proposed 4.75% APY high-yield CD lock for 12 months.",
        proposed_offer="4.75% APY 12-Month CD"
    )

    # 6. Progress to Retained
    service.update_case(
        case_id=case_id,
        new_status="Retained",
        performed_by="RM Sarah",
        notes="Customer accepted high-yield CD offer; funds retained in full."
    )

    # 7. Verify action audit history
    history = service.get_case_action_history(case_id)
    assert len(history) >= 4
    statuses_in_history = [h["new_status"] for h in history]
    assert "Retained" in statuses_in_history
    assert "Offer Proposed" in statuses_in_history
    assert "Contacted" in statuses_in_history
    assert "Assigned" in statuses_in_history

    # 8. Verify funnel
    funnel = service.get_funnel_analytics()
    assert funnel["total_cases"] > 0
    assert funnel["retained_count"] >= 1

