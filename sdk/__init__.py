"""
BankSight Official Python SDK
Enterprise client library for Core Banking, CRM, and FinTech systems integration.
"""

from sdk.banksight_client import (
    BankSightClient,
    BankSightSDKError,
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError,
    APIResponseError
)

__version__ = "2.0.0"
__all__ = [
    "BankSightClient",
    "BankSightSDKError",
    "AuthenticationError",
    "PermissionDeniedError",
    "ResourceNotFoundError",
    "APIResponseError"
]
