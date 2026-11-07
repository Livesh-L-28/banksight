"""
BankSight Executive KPI Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db, require_roles, log_api_action
from backend.api.schemas import ExecutiveKPISchema, BranchRankingSchema, ReconciliationSchema
from backend.repositories.kpi_repo import KPIRepository
from backend.repositories.branch_repo import BranchRepository
from backend.repositories.transaction_repo import TransactionRepository

router = APIRouter(prefix="/kpi", tags=["Executive Portfolio Intelligence"])


@router.get("/executive", response_model=ExecutiveKPISchema)
def get_executive_kpis(
    request: Request,
    branch_id: Optional[str] = Query(None, description="Optional branch filter"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Computes real-time executive banking KPIs. BranchManagers are automatically scoped to their branch.
    """
    effective_branch = user.get("branch_id") if user.get("role") == "BranchManager" else branch_id
    repo = KPIRepository(db)
    branch_ids = [effective_branch] if effective_branch else None
    kpis = repo.calculate_executive_kpis(branch_ids=branch_ids)
    kpis["net_flow"] = round(kpis.get("total_deposits", 0.0) - kpis.get("total_withdrawals", 0.0), 2)

    log_api_action(request, user, "VIEW_EXECUTIVE_KPIS", "PORTFOLIO", effective_branch or "ALL")
    return ExecutiveKPISchema(**kpis)


@router.get("/branch-rankings", response_model=List[BranchRankingSchema])
def get_branch_rankings(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Returns ranked operational efficiency benchmarks across all regional branches.
    """
    repo = BranchRepository(db)
    rankings = repo.get_branch_rankings()
    log_api_action(request, user, "VIEW_BRANCH_RANKINGS", "BRANCH", "ALL")
    return [BranchRankingSchema(**b) for b in rankings]


@router.get("/reconciliation", response_model=ReconciliationSchema)
def get_reconciliation(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "ComplianceOfficer"]))
):
    """
    Performs ledger reconciliation across credits, debits, and net clearing totals.
    """
    repo = TransactionRepository(db)
    rec = repo.run_reconciliation_audit()
    log_api_action(request, user, "PERFORM_RECONCILIATION", "TRANSACTIONS", "PORTFOLIO")
    return ReconciliationSchema(
        raw_transaction_count=rec["record_count"],
        raw_transaction_sum=rec["total_value"],
        credit_total=rec["credit_total"],
        debit_total=rec["debit_total"],
        net_clearing_balance=rec["net_clearing_balance"],
        reconciliation_status=rec["reconciliation_status"]
    )
