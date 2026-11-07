"""
BankSight Customer Lifetime Value (CLV) & Uplift Modeling Router
Provides discounted cash flow valuations, retention treatment quadrants,
and maximum allowable concession calculations.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, require_roles, log_api_action
from backend.models import Customer, Account, ChurnPrediction
from analytics.clv.uplift_engine import CustomerLifetimeValueEngine
from backend.monitoring.telemetry import portfolio_clv_36m_usd, clv_at_risk_usd

router = APIRouter(prefix="/clv", tags=["Customer Lifetime Value & Uplift Modeling"])


@router.get("/customer/{customer_id}")
def get_customer_clv_and_uplift(
    customer_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager", "DataAnalyst"]))
):
    """
    Computes discounted 12-month and 36-month CLV, retention treatment quadrant,
    and maximum allowable financial concession for a specific customer.
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer '{customer_id}' not found")

    accounts = db.query(Account).filter(Account.customer_id == customer_id).all()
    tot_bal = sum(a.current_balance for a in accounts) if accounts else 0.0

    pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).first()
    churn_prob = pred.churn_probability if pred else (0.85 if customer.churn_flag else 0.12)

    clv_result = CustomerLifetimeValueEngine.calculate_customer_clv(
        total_balance=tot_bal,
        churn_probability=churn_prob,
        annual_income=customer.annual_income or 65000.0,
        loan_count=len(customer.loans) if customer.loans else 0
    )

    log_api_action(request, user, "VIEW_CUSTOMER_CLV_UPLIFT", "CUSTOMER", customer_id)
    return {
        "customer_id": customer.customer_id,
        "customer_name": f"{customer.first_name} {customer.last_name}",
        "branch_id": customer.branch_id,
        "customer_segment": customer.customer_segment,
        **clv_result
    }


@router.get("/portfolio-summary")
def get_portfolio_clv_summary(
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Returns aggregate portfolio 36-month CLV, value at risk, and retention uplift quadrant distributions.
    """
    summary = CustomerLifetimeValueEngine.evaluate_portfolio_clv()
    if "error" in summary:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=summary["error"])

    log_api_action(request, user, "VIEW_PORTFOLIO_CLV_SUMMARY", "PORTFOLIO", "ALL")
    # Update Prometheus gauges
    portfolio_clv_36m_usd.set(summary.get("portfolio_36m_clv_usd", 0.0))
    clv_at_risk_usd.set(summary.get("clv_at_risk_usd", 0.0))

    # Exclude full_dataframe from JSON serialization
    res = {k: v for k, v in summary.items() if k != "full_dataframe"}
    return res
