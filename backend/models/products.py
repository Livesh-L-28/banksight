"""
Product & Lending Entities: Product, CustomerProduct, Loan.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Date, DateTime, Boolean, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from backend.database.connection import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True)
    product_code = Column(String(30), unique=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # Deposit, Loan, Card, Wealth
    annual_fee = Column(Float, default=0.0, nullable=False)
    interest_rate_pct = Column(Float, default=0.0, nullable=False)
    target_segment = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer_products = relationship("CustomerProduct", back_populates="product")
    loans = relationship("Loan", back_populates="product")


class CustomerProduct(Base):
    __tablename__ = "customer_products"

    cust_prod_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    enrollment_date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="Active", nullable=False, index=True)  # Active, Inactive, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="customer_products")
    product = relationship("Product", back_populates="customer_products")

    __table_args__ = (
        Index("idx_cust_prod_unique", "customer_id", "product_id"),
    )


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(String(50), primary_key=True)
    loan_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    principal_amount = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    interest_rate_pct = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    monthly_installment = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(30), default="Current", nullable=False, index=True)  # Current, Delinquent, Paid_Off, Defaulted
    delinquency_days = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="loans")
    product = relationship("Product", back_populates="loans")
