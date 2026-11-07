"""
BankSight Customer 360 Router with ABAC / Dynamic Masking
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db, require_roles, log_api_action
from backend.api.schemas import CustomerDetailSchema, CustomerTimelineItem
from backend.services.customer_service import CustomerService
from backend.security.pii_masker import PIIMasker

router = APIRouter(prefix="/customers", tags=["Customer 360 & Demographics"])


@router.get("/", response_model=List[dict])
def list_customers(
    request: Request,
    branch_id: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Searches customers with role-based branch scoping and dynamic PII privacy masking.
    """
    user_role = user.get("role")
    effective_branch = user.get("branch_id") if user_role == "BranchManager" else branch_id

    service = CustomerService()
    customers = service.search_customers(branch_id=effective_branch, segment=segment, limit=limit)

    # Apply row-level scoping for Relationship Managers
    if user_role == "RelationshipManager" and user.get("rm_id"):
        rm_id = user["rm_id"]
        customers = [c for c in customers if c.get("rm_id") == rm_id]

    # Apply PII dynamic masking based on role
    masked_customers = [PIIMasker.mask_customer_dossier(c, role=user_role) for c in customers]

    log_api_action(request, user, "SEARCH_CUSTOMERS", "CUSTOMER_LIST", f"count={len(masked_customers)}")
    return masked_customers


@router.get("/{customer_id}", response_model=CustomerDetailSchema)
def get_customer_dossier(
    customer_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Fetches full customer 360 intelligence profile with ABAC scoping and audit logging.
    """
    service = CustomerService()
    dossier = service.get_customer_dossier(customer_id)

    if not dossier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer '{customer_id}' not found")

    user_role = user.get("role")

    # Enforce Branch Isolation for Branch Managers
    if user_role == "BranchManager" and user.get("branch_id"):
        if dossier.get("branch_id") != user["branch_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You are only authorized to inspect customer profiles within your assigned branch."
            )

    # Apply role-based dynamic masking
    masked = PIIMasker.mask_customer_dossier(dossier, role=user_role)

    log_api_action(request, user, "VIEW_CUSTOMER_DOSSIER", "CUSTOMER", customer_id)
    return CustomerDetailSchema(**masked)


@router.get("/{customer_id}/timeline", response_model=List[CustomerTimelineItem])
def get_customer_timeline(
    customer_id: str,
    request: Request,
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager", "DataAnalyst", "ComplianceOfficer"]))
):
    """
    Retrieves chronologically sorted multi-channel customer activity timeline.
    """
    service = CustomerService()
    dossier = service.get_customer_dossier(customer_id)
    if not dossier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer '{customer_id}' not found")

    timeline = dossier.get("timeline", [])[:limit]
    log_api_action(request, user, "VIEW_CUSTOMER_TIMELINE", "CUSTOMER", customer_id)
    return [CustomerTimelineItem(**item) for item in timeline]
