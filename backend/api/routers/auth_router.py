"""
BankSight Authentication Router
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from backend.api.auth import (
    verify_password, create_access_token, ENTERPRISE_USERS
)
from backend.api.schemas import TokenResponse, UserProfile, LoginRequest
from backend.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Identity & Access Management"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, getting an access token for future requests.
    """
    user = ENTERPRISE_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "branch_id": user.get("branch_id"),
            "rm_id": user.get("rm_id")
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        username=user["username"],
        full_name=user["full_name"],
        branch_id=user.get("branch_id"),
        rm_id=user.get("rm_id")
    )


@router.post("/login", response_model=TokenResponse)
def login_json(payload: LoginRequest):
    """
    JSON-body compatible authentication endpoint.
    """
    user = ENTERPRISE_USERS.get(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "branch_id": user.get("branch_id"),
            "rm_id": user.get("rm_id")
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        username=user["username"],
        full_name=user["full_name"],
        branch_id=user.get("branch_id"),
        rm_id=user.get("rm_id")
    )


@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated user's profile and authorized banking scope."""
    return UserProfile(
        username=current_user["username"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        email=current_user["email"],
        branch_id=current_user.get("branch_id"),
        rm_id=current_user.get("rm_id")
    )
