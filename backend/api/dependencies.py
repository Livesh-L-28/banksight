"""
BankSight FastAPI Dependency Providers
Implements DB session injection, JWT verification, RBAC guardrails, and automated audit trails.
"""

from typing import List, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.api.auth import decode_access_token, ENTERPRISE_USERS
from backend.security.audit_logger import audit_logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a managed SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts and validates the current user identity and enterprise roles from the JWT bearer token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid, expired, or corrupted authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except Exception:
        raise credentials_exception from None

    user = ENTERPRISE_USERS.get(username)
    if user is None:
        raise credentials_exception

    return user


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory enforcing strict Role-Based Access Control (RBAC).
    """
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in allowed_roles and user_role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role '{user_role}' is not authorized. Required: {allowed_roles}"
            )
        return current_user
    return role_checker


def log_api_action(
    request: Request,
    user: dict,
    action: str,
    resource_type: str,
    resource_id: str,
    status_str: str = "SUCCESS"
):
    """Utility helper to record an immutable audit log entry for the action."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_logger.log_event(
        user_id=user["username"],
        role=user["role"],
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        client_ip=client_ip,
        status=status_str
    )
