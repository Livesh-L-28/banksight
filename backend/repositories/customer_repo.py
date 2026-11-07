"""
BankSight Customer 360 Repository
Fetches customer profiles, multi-account portfolios, chronological activity timelines, and interactions.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from backend.models import Customer, Account, Transaction, Complaint, CustomerInteraction, Branch, Loan, RelationshipManager


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def search_customers(
        self,
        search_query: Optional[str] = None,
        branch_id: Optional[str] = None,
        segment: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Searches customers with optional filtering and pagination."""
        query = self.session.query(Customer).join(Branch, Customer.branch_id == Branch.branch_id)

        if search_query:
            pattern = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    Customer.customer_id.ilike(pattern),
                    Customer.first_name.ilike(pattern),
                    Customer.last_name.ilike(pattern),
                    Customer.email.ilike(pattern),
                    Customer.city.ilike(pattern)
                )
            )
        if branch_id and branch_id != "All":
            query = query.filter(Customer.branch_id == branch_id)
        if segment and segment != "All":
            query = query.filter(Customer.customer_segment == segment)
        if status and status != "All":
            query = query.filter(Customer.customer_status == status)

        customers = query.order_by(Customer.customer_id.asc()).offset(offset).limit(limit).all()

        results = []
        for c in customers:
            total_bal = sum(a.current_balance for a in c.accounts) if c.accounts else 0.0
            results.append({
                "customer_id": c.customer_id,
                "full_name": f"{c.first_name} {c.last_name}",
                "age": c.age,
                "gender": c.gender,
                "occupation": c.occupation,
                "annual_income": c.annual_income,
                "city": c.city,
                "state": c.state,
                "customer_segment": c.customer_segment,
                "customer_status": c.customer_status,
                "churn_flag": c.churn_flag,
                "branch_name": c.branch.branch_name if c.branch else "N/A",
                "total_balance": round(total_bal, 2),
                "account_count": len(c.accounts)
            })
        return results

    def get_customer_dossier(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full Customer 360 intelligence dossier."""
        c = self.session.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not c:
            return None

        # Accounts
        accounts_data = [
            {
                "account_id": a.account_id,
                "account_number": a.account_number,
                "account_type": a.account_type.type_name if a.account_type else "Checking",
                "current_balance": a.current_balance,
                "available_balance": a.available_balance,
                "status": a.account_status,
                "currency": "USD",
                "open_date": a.open_date.isoformat(),
                "is_primary": a.is_primary
            }
            for a in c.accounts
        ]

        # Loans
        loans_data = [
            {
                "loan_id": loan.loan_id,
                "loan_number": loan.loan_number,
                "product_name": loan.product.product_name if loan.product else "Loan",
                "principal": loan.principal_amount,
                "current_balance": loan.current_balance,
                "interest_rate": loan.interest_rate_pct,
                "installment": loan.monthly_installment,
                "status": loan.status,
                "start_date": loan.start_date.isoformat(),
                "end_date": loan.end_date.isoformat()
            }
            for loan in c.loans
        ]

        # Recent transactions (up to 30)
        txns = self.session.query(Transaction).filter(Transaction.customer_id == customer_id)\
                   .order_by(Transaction.transaction_date.desc()).limit(30).all()
        txns_data = [
            {
                "transaction_id": t.transaction_id,
                "transaction_date": t.transaction_date.isoformat(),
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "balance_after": t.balance_after,
                "channel": t.channel,
                "status": t.status,
                "description": t.description
            }
            for t in txns
        ]

        # Complaints
        complaints_data = [
            {
                "complaint_id": comp.complaint_id,
                "category": comp.category,
                "priority": comp.priority,
                "status": comp.status,
                "logged_date": comp.logged_date.isoformat(),
                "resolved_date": comp.resolved_date.isoformat() if comp.resolved_date else None,
                "description": comp.description
            }
            for comp in c.complaints
        ]

        # Timeline chronological events (combine transactions, complaints, interactions)
        timeline = []
        for t in txns[:15]:
            timeline.append({
                "date": t.transaction_date.isoformat(),
                "event_type": f"Transaction ({t.transaction_type})",
                "channel": t.channel,
                "details": f"${t.amount:,.2f} - {t.description}"
            })
        for comp in c.complaints:
            timeline.append({
                "date": comp.logged_date.isoformat(),
                "event_type": "Complaint Logged",
                "channel": "Support Desk",
                "details": f"[{comp.priority} Priority] {comp.category}: {comp.description}"
            })
        for inter in c.interactions:
            timeline.append({
                "date": inter.interaction_date.isoformat(),
                "event_type": f"Interaction ({inter.sentiment})",
                "channel": inter.channel,
                "details": f"{inter.interaction_type}: {inter.summary or ''}"
            })

        # Sort timeline descending
        timeline.sort(key=lambda x: x["date"], reverse=True)

        total_balance = sum(a["current_balance"] for a in accounts_data)

        return {
            "customer_id": c.customer_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "full_name": f"{c.first_name} {c.last_name}",
            "email": c.email,
            "phone": c.phone,
            "date_of_birth": c.date_of_birth.isoformat(),
            "age": c.age,
            "gender": c.gender,
            "occupation": c.occupation,
            "annual_income": c.annual_income,
            "address": c.address,
            "city": c.city,
            "state": c.state,
            "postal_code": c.postal_code,
            "joining_date": c.joining_date.isoformat(),
            "tenure_months": c.customer_tenure_months,
            "customer_status": c.customer_status,
            "customer_segment": c.customer_segment,
            "credit_score": c.credit_score,
            "digital_active": c.digital_banking_active,
            "mobile_active": c.mobile_banking_active,
            "churn_flag": c.churn_flag,
            "churn_date": c.churn_date.isoformat() if c.churn_date else None,
            "branch_id": c.branch_id,
            "branch_name": c.branch.branch_name if c.branch else "N/A",
            "relationship_manager_name": f"{c.relationship_manager.first_name} {c.relationship_manager.last_name}" if c.relationship_manager else "Unassigned",
            "relationship_manager": f"{c.relationship_manager.first_name} {c.relationship_manager.last_name}" if c.relationship_manager else "Unassigned",
            "churn_risk_category": "High Risk" if c.churn_flag else "Low Risk",
            "churn_probability": 0.85 if c.churn_flag else 0.12,
            "total_balance": round(total_balance, 2),
            "accounts": accounts_data,
            "loans": loans_data,
            "transactions": txns_data,
            "complaints": complaints_data,
            "timeline": timeline[:25]
        }
