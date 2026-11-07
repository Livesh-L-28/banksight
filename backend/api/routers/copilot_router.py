"""
BankSight GenAI Relationship Manager Copilot Router
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.api.dependencies import get_db, require_roles, log_api_action
from backend.services.customer_service import CustomerService
from backend.copilot.rm_copilot import RMCopilotService

router = APIRouter(prefix="/copilot", tags=["Generative AI Relationship Manager Copilot"])


@router.post("/briefing/{customer_id}")
def generate_customer_briefing(
    customer_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(["Admin", "Executive", "BranchManager", "RelationshipManager"]))
):
    """
    Synthesizes customer 360 holdings, transactions, complaints, and churn drivers into
    an executive meeting briefing dossier and personalized outreach draft.
    """
    customer_service = CustomerService()
    dossier = customer_service.get_customer_dossier(customer_id)

    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found."
        )

    actor_name = user.get("full_name") or user.get("username", "Relationship Manager")
    briefing = RMCopilotService.generate_meeting_briefing(dossier, actor_name=actor_name)

    log_api_action(request, user, "GENERATE_AI_RM_BRIEFING", "CUSTOMER", customer_id)
    return briefing

