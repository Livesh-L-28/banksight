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

    def submit_concession_offer(
        self,
        case_id: str,
        rm_name: str,
        rm_id: Optional[str],
        offer_name: str,
        financial_concession_value: float,
        rate_adjustment_bps: int = 0,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits a proposed retention concession.
        Enforces SOX 404 Four-Eyes Principle: concessions > $500 or > 50 bps are held in 'Pending Approval'.
        """
        requires_approval = (financial_concession_value > 500.0) or (rate_adjustment_bps > 50)
        new_status = "Pending Approval" if requires_approval else "Offer Proposed"

        with get_db_context() as session:
            case = session.query(RetentionCase).filter(RetentionCase.case_id == case_id).first()
            if not case:
                return {"success": False, "error": f"Case '{case_id}' not found"}

            old_status = case.status
            case.status = new_status
            case.proposed_offer = f"{offer_name} [Value: ${financial_concession_value:,.2f}, Adj: +{rate_adjustment_bps} bps]"
            case.updated_at = datetime.utcnow()

            action_type = "CONCESSION_SUBMITTED_FOR_APPROVAL" if requires_approval else "OFFER_PROPOSED"
            action_notes = notes or (
                f"Proposed '{offer_name}' with financial concession of ${financial_concession_value:,.2f} "
                f"and {rate_adjustment_bps} bps. "
                + ("Requires Dual Authorization from Branch Manager / Executive." if requires_approval else "Standard discretion applied.")
            )

            action = RetentionAction(
                action_id=f"ACT-OFR-{uuid.uuid4().hex[:10]}",
                case_id=case_id,
                action_type=action_type,
                performed_by=rm_name,
                previous_status=old_status,
                new_status=new_status,
                notes=action_notes,
                action_timestamp=datetime.utcnow()
            )
            session.add(action)
            session.commit()

            return {
                "success": True,
                "case_id": case_id,
                "status": new_status,
                "requires_approval": requires_approval,
                "financial_value": financial_concession_value,
                "rate_adjustment_bps": rate_adjustment_bps,
                "proposed_by": rm_name
            }

    def review_concession_approval(
        self,
        case_id: str,
        approver_name: str,
        approver_role: str,
        approved: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes dual-authorization decision by a Branch Manager, Executive, or Admin.
        Enforces strict segregation of duties (approver cannot be the submitting RM).
        """
        valid_roles = {"Admin", "Executive", "BranchManager"}
        if approver_role not in valid_roles:
            return {
                "success": False,
                "error": f"Role '{approver_role}' is not authorized. Four-Eyes approval requires BranchManager, Executive, or Admin."
            }

        with get_db_context() as session:
            case = session.query(RetentionCase).filter(RetentionCase.case_id == case_id).first()
            if not case:
                return {"success": False, "error": f"Case '{case_id}' not found"}

            if case.status != "Pending Approval":
                return {"success": False, "error": f"Case '{case_id}' is in status '{case.status}', not 'Pending Approval'"}

            # Check Segregation of Duties: Approver cannot be the same person who submitted the concession
            last_submitting_action = session.query(RetentionAction).filter(
                RetentionAction.case_id == case_id,
                RetentionAction.action_type.in_(["CONCESSION_SUBMITTED_FOR_APPROVAL", "RM Assignment", "Case Created"])
            ).order_by(RetentionAction.action_timestamp.desc()).first()

            if last_submitting_action and last_submitting_action.performed_by.lower() == approver_name.lower():
                return {
                    "success": False,
                    "error": "Segregation of duties violation: Approver cannot be the same individual who submitted the retention concession."
                }

            old_status = case.status
            new_status = "Offer Proposed" if approved else "Contacted"
            case.status = new_status
            case.updated_at = datetime.utcnow()

            action_type = "DUAL_AUTHORIZATION_APPROVED" if approved else "DUAL_AUTHORIZATION_REJECTED"
            action_notes = notes or (
                f"Dual authorization {'APPROVED' if approved else 'REJECTED'} by {approver_role} ({approver_name})."
            )

            action = RetentionAction(
                action_id=f"ACT-APV-{uuid.uuid4().hex[:10]}",
                case_id=case_id,
                action_type=action_type,
                performed_by=f"{approver_name} ({approver_role})",
                previous_status=old_status,
                new_status=new_status,
                notes=action_notes,
                action_timestamp=datetime.utcnow()
            )
            session.add(action)
            session.commit()

            return {
                "success": True,
                "case_id": case_id,
                "decision": "APPROVED" if approved else "REJECTED",
                "new_status": new_status,
                "reviewed_by": approver_name,
                "reviewer_role": approver_role
            }

