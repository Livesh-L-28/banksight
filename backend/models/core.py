"""
Core Banking Entities: Branches, Relationship Managers, Customers, Account Types, Accounts, Transactions.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Boolean, ForeignKey, Index, Text
)
from sqlalchemy.orm import relationship
from backend.database.connection import Base


class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(String(50), primary_key=True)
    branch_name = Column(String(100), nullable=False)
    branch_code = Column(String(20), unique=True, nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    postal_code = Column(String(20), nullable=False)
    region = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    relationship_managers = relationship("RelationshipManager", back_populates="branch")
    customers = relationship("Customer", back_populates="branch")
    accounts = relationship("Account", back_populates="branch")


class RelationshipManager(Base):
    __tablename__ = "relationship_managers"

    rm_id = Column(String(50), primary_key=True)
    branch_id = Column(String(50), ForeignKey("branches.branch_id"), nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30), nullable=False)
    portfolio_size = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    branch = relationship("Branch", back_populates="relationship_managers")
    customers = relationship("Customer", back_populates="relationship_manager")
    retention_cases = relationship("RetentionCase", back_populates="relationship_manager")


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer, nullable=False, index=True)
    gender = Column(String(20), nullable=False, index=True)
    occupation = Column(String(100), nullable=False, index=True)
    annual_income = Column(Float, nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(50), default="USA", nullable=False)
    joining_date = Column(Date, nullable=False, index=True)
    customer_tenure_months = Column(Integer, nullable=False)
    customer_status = Column(String(30), default="Active", nullable=False, index=True)
    customer_segment = Column(String(50), default="Standard", nullable=False, index=True)
    branch_id = Column(String(50), ForeignKey("branches.branch_id"), nullable=False, index=True)
    rm_id = Column(String(50), ForeignKey("relationship_managers.rm_id"), nullable=True, index=True)
    credit_score = Column(Integer, nullable=True)
    kyc_verified = Column(Boolean, default=True, nullable=False)
    digital_banking_active = Column(Boolean, default=True, nullable=False)
    mobile_banking_active = Column(Boolean, default=True, nullable=False)
    opt_in_marketing = Column(Boolean, default=True, nullable=False)
    churn_flag = Column(Boolean, default=False, nullable=False, index=True)
    churn_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    branch = relationship("Branch", back_populates="customers")
    relationship_manager = relationship("RelationshipManager", back_populates="customers")
    accounts = relationship("Account", back_populates="customer", cascade="all, delete-orphan")
    customer_products = relationship("CustomerProduct", back_populates="customer", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="customer", cascade="all, delete-orphan")
    interactions = relationship("CustomerInteraction", back_populates="customer", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="customer", cascade="all, delete-orphan")
    campaign_assignments = relationship("CampaignAssignment", back_populates="customer", cascade="all, delete-orphan")
    churn_predictions = relationship("ChurnPrediction", back_populates="customer", cascade="all, delete-orphan")
    segment_records = relationship("CustomerSegment", back_populates="customer", cascade="all, delete-orphan")
    retention_cases = relationship("RetentionCase", back_populates="customer", cascade="all, delete-orphan")


class AccountType(Base):
    __tablename__ = "account_types"

    type_id = Column(String(50), primary_key=True)
    type_name = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # Deposit, Credit, Investment
    interest_rate_pct = Column(Float, default=0.0, nullable=False)
    monthly_fee = Column(Float, default=0.0, nullable=False)
    minimum_balance_req = Column(Float, default=0.0, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    accounts = relationship("Account", back_populates="account_type")


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(String(50), primary_key=True)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    type_id = Column(String(50), ForeignKey("account_types.type_id"), nullable=False, index=True)
    branch_id = Column(String(50), ForeignKey("branches.branch_id"), nullable=False, index=True)
    currency = Column(String(10), default="USD", nullable=False)
    current_balance = Column(Float, default=0.0, nullable=False)
    available_balance = Column(Float, default=0.0, nullable=False)
    average_balance_90d = Column(Float, default=0.0, nullable=False)
    account_status = Column(String(30), default="Active", nullable=False, index=True)
    open_date = Column(Date, nullable=False, index=True)
    close_date = Column(Date, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="accounts")
    account_type = relationship("AccountType", back_populates="accounts")
    branch = relationship("Branch", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(50), primary_key=True)
    account_id = Column(String(50), ForeignKey("accounts.account_id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    branch_id = Column(String(50), ForeignKey("branches.branch_id"), nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    transaction_type = Column(String(30), nullable=False, index=True)  # Deposit, Withdrawal, Transfer, Payment, Fee
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    channel = Column(String(30), nullable=False, index=True)  # ATM, POS, ONLINE, MOBILE, BRANCH
    status = Column(String(20), default="Completed", nullable=False, index=True)  # Completed, Failed, Pending, Flagged
    description = Column(String(255), nullable=True)
    merchant_category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        Index("idx_txn_cust_date", "customer_id", "transaction_date"),
        Index("idx_txn_channel_type", "channel", "transaction_type"),
    )

