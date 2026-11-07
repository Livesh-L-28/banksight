"""
Unit Tests for BankSight Executive KPI Calculations & Mathematical Consistency
"""

import pytest
from backend.database.connection import get_db_session
from backend.repositories.kpi_repo import KPIRepository
from backend.repositories.transaction_repo import TransactionRepository
from backend.repositories.branch_repo import BranchRepository


@pytest.fixture(scope="module")
def db_session():
    """Provides a session connected to the seeded database."""
    session = get_db_session()
    yield session
    session.close()


def test_executive_kpi_calculation(db_session):
    repo = KPIRepository(db_session)
    kpis = repo.calculate_executive_kpis()

    assert kpis["total_customers"] > 0
    assert kpis["total_accounts"] >= kpis["total_customers"]
    assert kpis["active_customers"] + kpis["inactive_customers"] == kpis["total_customers"]
    assert round(kpis["churn_rate_pct"] + kpis["retention_rate_pct"], 1) == 100.0
    assert kpis["total_deposits"] > 0
    assert kpis["total_withdrawals"] > 0
    assert kpis["total_transaction_value"] == round(kpis["total_deposits"] + kpis["total_withdrawals"], 2)
    assert kpis["average_customer_balance"] > 0
    assert kpis["arpu"] > 0
    assert kpis["customer_lifetime_value"] > 0


def test_executive_kpi_branch_filter(db_session):
    repo = KPIRepository(db_session)
    all_kpis = repo.calculate_executive_kpis()

    # Filter by specific branch
    branch_kpis = repo.calculate_executive_kpis(branch_ids=["BRN-001"])
    assert branch_kpis["total_customers"] > 0
    assert branch_kpis["total_customers"] < all_kpis["total_customers"]
    assert branch_kpis["total_deposits"] < all_kpis["total_deposits"]


def test_transaction_reconciliation(db_session):
    txn_repo = TransactionRepository(db_session)
    audit = txn_repo.run_reconciliation_audit()

    assert audit["total_transaction_records"] > 0
    assert audit["total_deposit_amount"] > 0
    assert audit["total_withdrawal_amount"] > 0
    assert audit["duplicate_transactions_found"] == 0
    assert audit["negative_balance_accounts"] == 0
    assert audit["reconciliation_status"] == "Balanced & Verified"


def test_branch_rankings(db_session):
    branch_repo = BranchRepository(db_session)
    rankings = branch_repo.get_branch_rankings()

    assert len(rankings) == 10
    # First ranked branch should have >= deposits than subsequent
    assert rankings[0]["total_deposits"] >= rankings[1]["total_deposits"]
    assert rankings[0]["rank"] == 1

