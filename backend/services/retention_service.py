"""
BankSight Operational Retention Management Service
Coordinates retention case workflows, RM assignment, status progression,
action audit tracking, and retention funnel conversions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid
from backend.database.connection import get_db_context
from backend.repositories.retention_repo import RetentionRepository
from backend.models import RetentionCase, RetentionAction, RelationshipManager


class RetentionService:
    def __init__(self):
        pass

    def get_cases(
        self,
        status_filter: Optional[str] = None,
        risk_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves retention cases with customer details and assigned RMs."""
        with get_db_context() as session:
            repo = RetentionRepository(session)
            return repo.get_retention_cases(status_filter, risk_filter)

    def create_retention_case(
        self,
        customer_id: str,
        churn_probability: float,
        risk_level: str = "High Risk",
        churn_reason: Optional[str] = None,
        recommended_action: Optional[str] = None,
        rm_id: Optional[str] = None,
        follow_up_date: Optional[date] = None
    ) -> str:
        """Opens a new retention case and records creation audit log."""
        with get_db_context() as session:
            repo = RetentionRepository(session)
            case_id = repo.create_case(
                customer_id=customer_id,
                churn_probability=churn_probability,
                risk_level=risk_level,
                churn_reason=churn_reason,
                recommended_action=recommended_action,
                rm_id=rm_id,
                follow_up_date=follow_up_date
            )
            return case_id

    def update_case(
        self,
        case_id: str,
        new_status: str,
        performed_by: str,
        notes: str,
        proposed_offer: Optional[str] = None
    ) -> bool:
        """Transitions case status, updates proposed offer, and logs action entry."""
        with get_db_context() as session:
            repo = RetentionRepository(session)
            return repo.update_case_status(
                case_id=case_id,
                new_status=new_status,
                performed_by=performed_by,
                notes=notes,
                proposed_offer=proposed_offer
            )

    def assign_relationship_manager(
        self,
        case_id: str,
        rm_id: str,
        performed_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Assigns RM to a case and advances status to Assigned if currently Identified."""
        with get_db_context() as session:
            case = session.query(RetentionCase).filter(RetentionCase.case_id == case_id).first()
            if not case:
                return False

            old_rm = case.rm_id
            old_status = case.status
            case.rm_id = rm_id
            if case.status == "Identified":
                case.status = "Assigned"

            action = RetentionAction(
                action_id=f"ACT-ASG-{uuid.uuid4().hex[:10]}",
                case_id=case_id,
                action_type="RM Assignment",
                performed_by=performed_by,
                previous_status=old_status,
                new_status=case.status,
                notes=notes or f"Assigned to RM {rm_id}",
                action_timestamp=datetime.utcnow()
            )
            session.add(action)
            session.commit()
            return True

    def get_funnel_analytics(self) -> Dict[str, Any]:
        """Calculates retention funnel stages and overall retention conversion rate."""
        with get_db_context() as session:
            repo = RetentionRepository(session)
            funnel = repo.get_funnel_summary()

            total_cases = sum(funnel.values())
            contacted_or_beyond = funnel["Contacted"] + funnel["Offer Proposed"] + funnel["Retained"] + funnel["Not Retained"] + funnel["Closed"]
            retained_count = funnel["Retained"]

            conversion_rate = round((retained_count / max(contacted_or_beyond, 1)) * 100, 2) if contacted_or_beyond > 0 else 0.0

            return {
                "funnel_counts": funnel,
                "total_cases": total_cases,
                "contacted_or_beyond": contacted_or_beyond,
                "retained_count": retained_count,
                "retention_conversion_rate": conversion_rate
            }

    def get_case_action_history(self, case_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological audit trail of all actions performed on a case."""
        with get_db_context() as session:
            actions = session.query(RetentionAction).filter(RetentionAction.case_id == case_id)\
                             .order_by(RetentionAction.action_timestamp.desc()).all()
            return [
                {
                    "action_id": a.action_id,
                    "action_type": a.action_type,
                    "performed_by": a.performed_by,
                    "previous_status": a.previous_status,
                    "new_status": a.new_status,
                    "notes": a.notes,
                    "timestamp": a.action_timestamp.isoformat()
                }
                for a in actions
            ]
