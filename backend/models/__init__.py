"""
BankSight Relational Model Registry: Exposes all 21 entities and declarative Base.
"""

from backend.database.connection import Base
from backend.models.core import (
    Branch,
    RelationshipManager,
    Customer,
    AccountType,
    Account,
    Transaction,
)
from backend.models.products import (
    Product,
    CustomerProduct,
    Loan,
)
from backend.models.engagement import (
    CustomerInteraction,
    Complaint,
)
from backend.models.campaigns import (
    Campaign,
    CampaignAssignment,
    CampaignResponse,
)
from backend.models.intelligence import (
    CustomerSegment,
    ModelVersion,
    ChurnPrediction,
)
from backend.models.retention import (
    RetentionCase,
    RetentionAction,
)
from backend.models.pipeline import (
    DataImportJob,
    DataQualityResult,
)

__all__ = [
    "Base",
    "Branch",
    "RelationshipManager",
    "Customer",
    "AccountType",
    "Account",
    "Transaction",
    "Product",
    "CustomerProduct",
    "Loan",
    "CustomerInteraction",
    "Complaint",
    "Campaign",
    "CampaignAssignment",
    "CampaignResponse",
    "CustomerSegment",
    "ModelVersion",
    "ChurnPrediction",
    "RetentionCase",
    "RetentionAction",
    "DataImportJob",
    "DataQualityResult",
]
