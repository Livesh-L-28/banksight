"""
BankSight Retention Management Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db, require_roles, log_api_action
from backend.api.schemas import (
    RetentionCaseSchema, RetentionTransitionRequest, RetentionFunnelMetrics,
    ConcessionSubmissionRequest, ConcessionApprovalRequest
)
from backend.services.retention_service import RetentionService

router = APIRouter(prefix="/retention", tags=["Closed-Loop Retention Management"])


@router.get("/cases", response_model=List[RetentionCaseSchema])
def list_retention_cases(
    request: Request,
    branch_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager", "DataAnalyst"]))
):
    """
    Lists operational retention cases scoped by branch and assigned relationship manager.
    """
    user_role = user.get("role")
    effective_branch = user.get("branch_id") if user_role == "BranchManager" else branch_id
    effective_rm = user.get("rm_id") if user_role == "RelationshipManager" else None

    service = RetentionService()
    cases = service.list_cases(
        branch_id=effective_branch,
        rm_id=effective_rm,
        status=status_filter,
        priority=priority,
        limit=limit
    )

    log_api_action(request, user, "LIST_RETENTION_CASES", "RETENTION_PORTFOLIO", f"count={len(cases)}")
    return [RetentionCaseSchema(**c) for c in cases]


@router.get("/cases/{case_id}")
def get_retention_case_detail(
    case_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager"]))
):
    """
    Retrieves retention case details along with its complete chronological audit action log.
    """
    service = RetentionService()
    case_detail = service.get_case_detail(case_id)
    if not case_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Retention case '{case_id}' not found")

    log_api_action(request, user, "VIEW_RETENTION_CASE", "RETENTION_CASE", case_id)
    return case_detail


@router.post("/cases/{case_id}/transition")
def transition_case_status(
    case_id: str,
    payload: RetentionTransitionRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "BranchManager", "RelationshipManager"]))
):
    """
    Executes a validated lifecycle status transition and appends an immutable action log.
    """
    service = RetentionService()
    result = service.transition_case_status(
        case_id=case_id,
        new_status=payload.new_status,
        action_type=payload.action_type,
        actor_name=user.get("full_name", user["username"]),
        outcome=payload.outcome,
        notes=payload.notes,
        follow_up_date=payload.follow_up_date,
        reassigned_rm_id=payload.reassigned_rm_id
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Transition failed"))

    log_api_action(
        request, user, f"TRANSITION_CASE_TO_{payload.new_status.upper()}", "RETENTION_CASE", case_id
    )
    return result


@router.get("/funnel", response_model=RetentionFunnelMetrics)
def get_retention_funnel(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Returns aggregate funnel conversion metrics across all operational retention cases.
    """
    service = RetentionService()
    funnel = service.get_funnel_analytics()
    log_api_action(request, user, "VIEW_RETENTION_FUNNEL", "RETENTION_FUNNEL", "PORTFOLIO")
    return RetentionFunnelMetrics(**funnel)


@router.post("/cases/{case_id}/submit-concession")
def submit_concession_offer(
    case_id: str,
    payload: ConcessionSubmissionRequest,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "BranchManager", "RelationshipManager"]))
):
    """
    Submits a proposed retention concession.
    Enforces SOX 404 Four-Eyes Principle: concessions > $500 or > 50 bps are held in 'Pending Approval'.
    """
    service = RetentionService()
    result = service.submit_concession_offer(
        case_id=case_id,
        rm_name=user.get("full_name") or user.get("username"),
        rm_id=user.get("rm_id"),
        offer_name=payload.offer_name,
        financial_concession_value=payload.financial_concession_value,
        rate_adjustment_bps=payload.rate_adjustment_bps,
        notes=payload.notes
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Submission failed"))

    action_label = "SUBMIT_CONCESSION_FOR_APPROVAL" if result.get("requires_approval") else "OFFER_PROPOSED"
    log_api_action(request, user, action_label, "RETENTION_CASE", case_id)
    return result


@router.post("/cases/{case_id}/review-approval")
def review_concession_approval(
    case_id: str,
    payload: ConcessionApprovalRequest,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager"]))
):
    """
    Executes Four-Eyes Principle dual authorization on a pending retention concession.
    Strictly verifies segregation of duties (approver cannot be the submitting RM).
    """
    service = RetentionService()
    result = service.review_concession_approval(
        case_id=case_id,
        approver_name=user.get("full_name") or user.get("username"),
        approver_role=user.get("role"),
        approved=payload.approved,
        notes=payload.notes
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Review failed"))

    decision_label = "APPROVE_DUAL_AUTHORIZATION" if payload.approved else "REJECT_DUAL_AUTHORIZATION"
    log_api_action(request, user, decision_label, "RETENTION_CASE", case_id)
    return result


@router.get("/pending-approvals", response_model=List[RetentionCaseSchema])
def list_pending_approvals(
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager"]))
):
    """
    Lists all retention cases currently pending senior manager dual authorization.
    """
    service = RetentionService()
    cases = service.list_cases(status="Pending Approval")
    log_api_action(request, user, "LIST_PENDING_APPROVALS", "RETENTION_PORTFOLIO", f"count={len(cases)}")
    return [RetentionCaseSchema(**c) for c in cases]

