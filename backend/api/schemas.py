"""
BankSight Pydantic v2 Request & Response Data Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ==========================================
# Authentication & Identity Schemas
# ==========================================

class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="Admin@123")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: str
    branch_id: Optional[str] = None
    rm_id: Optional[str] = None


class UserProfile(BaseModel):
    username: str
    full_name: str
    role: str
    email: str
    branch_id: Optional[str] = None
    rm_id: Optional[str] = None


# ==========================================
# Executive KPI Schemas
# ==========================================

class ExecutiveKPISchema(BaseModel):
    total_customers: int
    active_customers: int
    inactive_customers: int
    new_customers: int = 0
    total_accounts: int
    total_deposits: float
    total_withdrawals: float
    total_transaction_value: float
    average_customer_balance: float = 0.0
    arpu: float = 0.0
    churn_rate_pct: float
    retention_rate_pct: float
    customer_lifetime_value: float = 0.0
    high_risk_customers: int = 0
    campaign_conversion_rate: float = 0.0
    net_flow: float = 0.0

    model_config = {"populate_by_name": True}


class BranchRankingSchema(BaseModel):
    branch_id: str
    branch_name: str
    city: str
    region: str
    customer_count: int
    total_deposits: float
    avg_customer_balance: float
    churn_rate_pct: float
    rank: int


class ReconciliationSchema(BaseModel):
    raw_transaction_count: int
    raw_transaction_sum: float
    credit_total: float
    debit_total: float
    net_clearing_balance: float
    reconciliation_status: str


# ==========================================
# Customer Intelligence Schemas
# ==========================================

class CustomerAccountSummary(BaseModel):
    account_id: str
    account_type: str
    current_balance: float
    status: str
    currency: str


class CustomerDetailSchema(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    full_name: str
    gender: str
    age: int
    city: str
    state: str
    postal_code: str
    occupation: str
    annual_income: float
    tenure_months: int
    customer_segment: str
    branch_id: str
    branch_name: str
    relationship_manager_name: str
    churn_risk_category: str
    churn_probability: float
    accounts: List[CustomerAccountSummary]
    total_balance: float


class CustomerTimelineItem(BaseModel):
    timestamp: str
    category: str
    title: str
    amount: Optional[float] = None
    status: Optional[str] = None


# ==========================================
# Churn Prediction & Scoring Schemas
# ==========================================

class ChurnInferenceRequest(BaseModel):
    customer_id: str = Field(..., example="CUST-00001")
    tenure_months: int = Field(..., example=36)
    age: int = Field(..., example=42)
    annual_income: float = Field(..., example=85000.0)
    current_balance: float = Field(..., example=12450.0)
    balance_to_income_ratio: float = Field(..., example=0.146)
    txn_frequency_12m: int = Field(..., example=48)
    total_spend_12m: float = Field(..., example=9200.0)
    recency_days: int = Field(..., example=12)
    complaints_count: int = Field(default=0, example=1)
    digital_banking_active: bool = Field(default=True)
    mobile_banking_active: bool = Field(default=True)
    loan_count: int = Field(default=0)
    credit_card_count: int = Field(default=1)


class ChurnInferenceResponse(BaseModel):
    customer_id: str
    churn_probability: float
    churn_flag: bool
    risk_category: str  # Low Risk, Medium Risk, High Risk
    contributing_drivers: List[str]
    advisory_retention_action: str
    model_version: str


# ==========================================
# Retention Case Schemas
# ==========================================

class RetentionCaseSchema(BaseModel):
    case_id: str
    customer_id: str
    customer_name: str
    branch_id: str
    rm_id: str
    assigned_rm: str
    churn_probability: float
    risk_category: str
    status: str
    priority: str
    created_at: str
    updated_at: str


class RetentionTransitionRequest(BaseModel):
    new_status: str = Field(..., example="Contacted")
    action_type: str = Field(..., example="Customer Outreach Call")
    outcome: str = Field(..., example="Discussed financial plan")
    notes: Optional[str] = Field(None, example="Customer agreed to evaluate high-yield deposit offer.")
    follow_up_date: Optional[str] = None
    reassigned_rm_id: Optional[str] = None


class RetentionFunnelMetrics(BaseModel):
    total_cases: int
    contacted_or_beyond: int
    retained_count: int
    retention_conversion_rate: float
    funnel_counts: Dict[str, int]


class ConcessionSubmissionRequest(BaseModel):
    offer_name: str = Field(..., example="Premier High-Yield Savings Upgrade")
    financial_concession_value: float = Field(..., example=750.0, description="Financial concession value in USD")
    rate_adjustment_bps: int = Field(default=0, example=50, description="Interest rate bonus or cut in basis points")
    notes: Optional[str] = Field(None, example="Client requested rate matching against external commercial bank.")


class ConcessionApprovalRequest(BaseModel):
    approved: bool = Field(..., example=True)
    notes: Optional[str] = Field(None, example="Approved under branch executive pricing discretion.")



# ==========================================
# Governance & Audit Schemas
# ==========================================

class AuditLogItem(BaseModel):
    event_id: str
    timestamp_utc: str
    user_id: str
    role: str
    action: str
    resource_type: str
    resource_id: str
    client_ip: str
    status: str
    record_hash: str


class AuditIntegrityResponse(BaseModel):
    valid: bool
    count: int
    message: str
    error: Optional[str] = None
