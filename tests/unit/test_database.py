"""
Unit Tests for BankSight Relational Database Schema & Entities
"""

import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.connection import Base
from backend.models import (
    Branch, RelationshipManager, Customer, AccountType, Account, Transaction,
    Product, CustomerProduct, Loan, RetentionCase, RetentionAction
)


@pytest.fixture(scope="function")
def test_db():
    """In-memory SQLite test database fixture."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_branch_and_rm_creation(test_db):
    branch = Branch(
        branch_id="BRN-TEST-1",
        branch_name="Test Central Branch",
        branch_code="TCB01",
        address="100 Main St",
        city="Charlotte",
        state="NC",
        postal_code="28202",
        region="Southeast"
    )
    test_db.add(branch)
    test_db.commit()

    rm = RelationshipManager(
        rm_id="RM-TEST-1",
        branch_id=branch.branch_id,
        first_name="Alice",
        last_name="Walker",
        email="alice.walker@banksight.test",
        phone="555-0199",
        portfolio_size=15
    )
    test_db.add(rm)
    test_db.commit()

    assert rm.branch.branch_name == "Test Central Branch"
    assert len(branch.relationship_managers) == 1


def test_customer_and_account_creation(test_db):
    branch = Branch(
        branch_id="BRN-TEST-2",
        branch_name="Test Metro Branch",
        branch_code="TMB02",
        address="200 Market St",
        city="Atlanta",
        state="GA",
        postal_code="30303",
        region="Southeast"
    )
    test_db.add(branch)
    test_db.commit()

    customer = Customer(
        customer_id="CUST-TEST-1",
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        phone="555-0101",
        date_of_birth=date(1985, 5, 20),
        age=39,
        gender="Male",
        occupation="Software Engineer",
        annual_income=120000.0,
        address="500 Tech Blvd",
        city="Atlanta",
        state="GA",
        postal_code="30303",
        joining_date=date(2020, 1, 15),
        customer_tenure_months=52,
        customer_status="Active",
        branch_id=branch.branch_id
    )
    test_db.add(customer)

    acc_type = AccountType(
        type_id="TYPE-CHK",
        type_name="Premium Checking",
        category="Deposit",
        interest_rate_pct=0.05,
        monthly_fee=12.0,
        minimum_balance_req=1000.0
    )
    test_db.add(acc_type)
    test_db.commit()

    account = Account(
        account_id="ACC-TEST-1",
        account_number="CHK-998877",
        customer_id=customer.customer_id,
        type_id=acc_type.type_id,
        branch_id=branch.branch_id,
        current_balance=15420.50,
        available_balance=15420.50,
        average_balance_90d=14800.00,
        account_status="Active",
        open_date=date(2020, 1, 15),
        is_primary=True
    )
    test_db.add(account)
    test_db.commit()

    assert account.customer.first_name == "John"
    assert account.account_type.type_name == "Premium Checking"
    assert len(customer.accounts) == 1
    assert customer.accounts[0].current_balance == 15420.50


def test_retention_case_lifecycle(test_db):
    branch = Branch(
        branch_id="BRN-TEST-3",
        branch_name="North Branch",
        branch_code="NB03",
        address="300 Oak Ave",
        city="Raleigh",
        state="NC",
        postal_code="27601",
        region="Southeast"
    )
    test_db.add(branch)
    test_db.commit()

    customer = Customer(
        customer_id="CUST-TEST-2",
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@test.com",
        phone="555-0102",
        date_of_birth=date(1990, 8, 12),
        age=34,
        gender="Female",
        occupation="Marketing Director",
        annual_income=95000.0,
        address="700 Green St",
        city="Raleigh",
        state="NC",
        postal_code="27601",
        joining_date=date(2021, 6, 1),
        customer_tenure_months=35,
        customer_status="Active",
        branch_id=branch.branch_id
    )
    test_db.add(customer)
    test_db.commit()

    case = RetentionCase(
        case_id="CASE-TEST-1",
        customer_id=customer.customer_id,
        status="Identified",
        risk_level="High Risk",
        churn_probability=0.82,
        churn_reason="Significant balance drop and competitor interest"
    )
    test_db.add(case)
    test_db.commit()

    action = RetentionAction(
        action_id="ACT-TEST-1",
        case_id=case.case_id,
        action_type="Status Change",
        performed_by="RM Sarah",
        previous_status="Identified",
        new_status="Contacted",
        notes="Spoke with customer; discussed deposit interest boost."
    )
    case.status = "Contacted"
    test_db.add(action)
    test_db.commit()

    assert case.status == "Contacted"
    assert len(case.actions) == 1
    assert case.actions[0].new_status == "Contacted"
