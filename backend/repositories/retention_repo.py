"""
BankSight Retention Management Repository
Manages operational retention case lifecycle, RM assignments, status progressions, and audit actions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.models import RetentionCase, RetentionAction, Customer, RelationshipManager, Branch


class RetentionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_retention_cases(
        self,
        status_filter: Optional[str] = None,
        risk_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves active and closed retention cases."""
        query = self.session.query(RetentionCase)\
            .join(Customer, RetentionCase.customer_id == Customer.customer_id)\
            .outerjoin(RelationshipManager, RetentionCase.rm_id == RelationshipManager.rm_id)

        if status_filter and status_filter != "All":
            query = query.filter(RetentionCase.status == status_filter)
        if risk_filter and risk_filter != "All":
            query = query.filter(RetentionCase.risk_level == risk_filter)

        cases = query.order_by(RetentionCase.churn_probability.desc()).all()

        results = []
        for rc in cases:
            total_bal = sum(a.current_balance for a in rc.customer.accounts) if rc.customer and rc.customer.accounts else 0.0
            results.append({
                "case_id": rc.case_id,
                "customer_id": rc.customer_id,
                "customer_name": f"{rc.customer.first_name} {rc.customer.last_name}" if rc.customer else "Unknown",
                "customer_email": rc.customer.email if rc.customer else "N/A",
                "total_balance": round(total_bal, 2),
                "rm_id": rc.rm_id,
                "rm_name": f"{rc.relationship_manager.first_name} {rc.relationship_manager.last_name}" if rc.relationship_manager else "Unassigned",
                "status": rc.status,
                "risk_level": rc.risk_level,
                "churn_probability": round(rc.churn_probability, 3),
                "churn_reason": rc.churn_reason,
                "recommended_action": rc.recommended_action,
                "proposed_offer": rc.proposed_offer,
                "follow_up_date": rc.follow_up_date.isoformat() if rc.follow_up_date else None,
                "created_at": rc.created_at.isoformat(),
                "action_count": len(rc.actions)
            })
        return results

    def create_case(
        self,
        customer_id: str,
        churn_probability: float,
        risk_level: str = "High Risk",
        churn_reason: Optional[str] = None,
        recommended_action: Optional[str] = None,
        rm_id: Optional[str] = None,
        follow_up_date: Optional[date] = None
    ) -> str:
        """Creates a new operational retention case."""
        case_id = f"CASE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{customer_id[-4:]}"
        case = RetentionCase(
            case_id=case_id,
            customer_id=customer_id,
            rm_id=rm_id,
            status="Identified" if not rm_id else "Assigned",
            risk_level=risk_level,
            churn_probability=churn_probability,
            churn_reason=churn_reason or "Elevated predictive defection score",
            recommended_action=recommended_action or "Schedule relationship review meeting",
            follow_up_date=follow_up_date or (date.today() + (date(2026, 11, 7) - date.today() if hasattr(date, 'today') else None)),
            created_at=datetime.utcnow()
        )
        self.session.add(case)

        # Initial action log
        action = RetentionAction(
            action_id=f"ACT-{uuid.uuid4().hex[:10]}",
            case_id=case_id,
            action_type="Case Created",
            performed_by="Automated ML Early Warning",
            previous_status=None,
            new_status=case.status,
            notes="Case initialized from predictive churn queue.",
            action_timestamp=datetime.utcnow()
        )
        self.session.add(action)
        self.session.commit()
        return case_id

    def update_case_status(
        self,
        case_id: str,
        new_status: str,
        performed_by: str,
        notes: str,
        proposed_offer: Optional[str] = None
    ) -> bool:
        """Transitions case status, updates proposed offer, and logs action entry."""
        case = self.session.query(RetentionCase).filter(RetentionCase.case_id == case_id).first()
        if not case:
            return False

        old_status = case.status
        case.status = new_status
        if proposed_offer:
            case.proposed_offer = proposed_offer
        if new_status in ["Retained", "Not Retained", "Closed"]:
            case.closed_date = date.today()
        case.updated_at = datetime.utcnow()

        action = RetentionAction(
            action_id=f"ACT-{uuid.uuid4().hex[:10]}",
            case_id=case_id,
            action_type="Status Transition",
            performed_by=performed_by,
            previous_status=old_status,
            new_status=new_status,
            notes=notes,
            action_timestamp=datetime.utcnow()
        )
        self.session.add(action)
        self.session.commit()
        return True

    def get_funnel_summary(self) -> Dict[str, int]:
        """Calculates count of cases across retention lifecycle stages."""
        sql = """
        SELECT status, COUNT(case_id) as count
        FROM retention_cases
        GROUP BY status
        """
        rows = self.session.execute(text(sql)).fetchall()
        funnel = {
            "Identified": 0,
            "Assigned": 0,
            "Contacted": 0,
            "Offer Proposed": 0,
            "Retained": 0,
            "Not Retained": 0,
            "Closed": 0
        }
        for status, count in rows:
            if status in funnel:
                funnel[status] = int(count)
        return funnel
