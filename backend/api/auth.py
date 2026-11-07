"""
BankSight Authentication & Role-Based Access Control (RBAC)
Implements JWT token issuance, verification, and role assignments.
"""

import os
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt

JWT_SECRET = os.getenv("BANKSIGHT_JWT_SECRET", "banksight-enterprise-secret-key-prod-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12-hour session

# Enterprise Demo Users for testing & frontline demonstration
ENTERPRISE_USERS: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "password_hash": "816e7e36dd2874bd41d76861c66aede80cffbd7793c4ec918eecc2e413093d8e",  # "Admin@123"
        "full_name": "System Administrator",
        "role": "Admin",
        "branch_id": None,
        "rm_id": None,
        "email": "admin@banksight.internal"
    },
    "exec": {
        "username": "exec",
        "password_hash": "2ec697732f191776b5aefa75eb0170f7b2b44b879e5a664cbf5e527529f3d094",  # "Exec@123"
        "full_name": "Chief Banking Officer",
        "role": "Executive",
        "branch_id": None,
        "rm_id": None,
        "email": "cbo@banksight.internal"
    },
    "branch_mgr_1": {
        "username": "branch_mgr_1",
        "password_hash": "e76ad1b94cd2e4361b5d26d6ff18e85ad0d3aa8c6f66b441487b2007acb18a7f",  # "Branch@123"
        "full_name": "Marcus Aurelius (Downtown Branch)",
        "role": "BranchManager",
        "branch_id": "BR-001",
        "rm_id": None,
        "email": "marcus.br001@banksight.internal"
    },
    "rm_alex": {
        "username": "rm_alex",
        "password_hash": "2361eef9575482babe7413abd1575cfd796d17a0d56fc348cc52850f20ff7424",  # "Alex@123"
        "full_name": "Alexander Hamilton (Senior RM)",
        "role": "RelationshipManager",
        "branch_id": "BR-001",
        "rm_id": "RM-001",
        "email": "alexander.rm@banksight.internal"
    },
    "analyst": {
        "username": "analyst",
        "password_hash": "af90e0ec1b88ef576a8f11db76b438c8ac571cdebd5b77bf9dd26ca64241c537",  # "Analyst@123"
        "full_name": "Data Analytics Team",
        "role": "DataAnalyst",
        "branch_id": None,
        "rm_id": None,
        "email": "analyst@banksight.internal"
    },
    "compliance": {
        "username": "compliance",
        "password_hash": "083f8da9eff133e835c95c4408178adeb84d1aaa70d55ba3f3e48bc69b595e19",  # "Audit@123"
        "full_name": "Chief Compliance Officer",
        "role": "ComplianceOfficer",
        "branch_id": None,
        "rm_id": None,
        "email": "compliance@banksight.internal"
    }
}


def hash_password(password: str) -> str:
    """Computes SHA-256 password hash with internal salt."""
    salt = b"BankSight_Auth_Salt_2026"
    return hmac.new(salt, password.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verification of password against stored hash."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a cryptographically signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
