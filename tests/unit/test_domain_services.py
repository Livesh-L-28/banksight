"""
Unit Tests for Domain Services: Transactions, Campaigns, Branches, Products, Customer 360
"""

import pytest
from backend.services.transaction_service import TransactionService
from backend.services.campaign_service import CampaignService
from backend.services.branch_service import BranchService
from backend.services.product_service import ProductService
from backend.services.customer_service import CustomerService


def test_transaction_service():
    service = TransactionService()
    channels = service.get_channel_analytics()
    assert len(channels) > 0
    assert sum(c["total_volume"] for c in channels) > 0

    spend = service.get_spending_breakdown()
    assert len(spend) > 0

    dormant = service.get_dormant_accounts(days_threshold=90)
    assert isinstance(dormant, list)

    reconciliation = service.run_reconciliation()
    assert reconciliation["reconciliation_status"] == "Balanced & Verified"


def test_campaign_service():
    service = CampaignService()
    campaigns = service.get_campaign_performance()
    assert len(campaigns) == 5
    for c in campaigns:
        assert c["reach"] > 0
        assert c["budget"] > 0
        assert 0.0 <= c["response_rate_pct"] <= 100.0


def test_branch_service():
    service = BranchService()
    branches = service.get_all_branches()
    assert len(branches) == 10

    rankings = service.get_branch_rankings()
    assert len(rankings) == 10
    assert rankings[0]["rank"] == 1

    regional = service.get_regional_summary()
    assert len(regional) > 0


def test_product_service():
    service = ProductService()
    portfolio = service.get_portfolio_penetration()
    assert len(portfolio) >= 8

    cross_sells = service.get_cross_sell_leads()
    assert len(cross_sells) > 0
    assert "recommended_product" in cross_sells[0]


def test_customer_service():
    service = CustomerService()
    search_results = service.search_customers(search_query="CUST-00001", limit=5)
    assert len(search_results) == 1
    assert search_results[0]["customer_id"] == "CUST-00001"

    dossier = service.get_customer_dossier("CUST-00001")
    assert dossier is not None
    assert dossier["customer_id"] == "CUST-00001"
    assert len(dossier["accounts"]) >= 1
    assert len(dossier["timeline"]) > 0

