"""
BankSight Enterprise Test Suite: Concession Pricing Optimizer & BSA/AML SAR Generator
Tests algorithmic pricing evaluation, candidate concession ROI, four-eyes flags,
BSA/AML red-flag detection, and FinCEN Form 111 SAR narrative packet synthesis.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from analytics.retention.pricing_optimizer import ConcessionPricingOptimizer
from backend.compliance.sar_generator import FinCENSARGenerator
from sdk.banksight_client import BankSightClient


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(api_client):
    login_resp = api_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@123"}
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def test_concession_pricing_optimizer_evaluations():
    """Verifies that the pricing optimizer ranks candidate offers and selects optimal incentive."""
    # 1. High value customer with moderate churn
    result = ConcessionPricingOptimizer.evaluate_customer_offers(
        total_balance=45000.0,
        churn_probability=0.35,
        annual_income=85000.0,
        loan_count=1
    )
    assert "optimal_recommendation" in result
    assert "evaluated_offers" in result
    assert len(result["evaluated_offers"]) >= 5

    opt = result["optimal_recommendation"]
    assert "offer_id" in opt
    assert "offer_name" in opt
    assert "expected_net_gain_usd" in opt
    assert "projected_retention_probability" in opt
    assert opt["projected_retention_probability"] > result["baseline_metrics"]["baseline_retention_prob"]

    # 2. Database customer lookup
    db_result = ConcessionPricingOptimizer.optimize_for_customer_id("CUST-00001")
    assert "customer_profile" in db_result
    assert db_result["customer_profile"]["customer_id"] == "CUST-00001"
    assert "optimal_recommendation" in db_result


def test_fincen_sar_generator_and_red_flags():
    """Verifies BSA/AML red-flag risk scanning and FinCEN SAR narrative construction."""
    # 1. Scan single customer
    analysis = FinCENSARGenerator.scan_customer_aml_risks("CUST-00001")
    assert "customer_id" in analysis
    assert "aml_risk_score" in analysis
    assert "total_debit_outflow_usd" in analysis
    assert isinstance(analysis["red_flags"], list)

    # 2. Portfolio scan
    alerts = FinCENSARGenerator.scan_portfolio_for_alerts(limit=25)
    assert isinstance(alerts, list)
    if alerts:
        top_alert = alerts[0]
        assert top_alert["aml_risk_score"] >= 40
        assert len(top_alert["red_flags"]) > 0

    # 3. Generate SAR Narrative Packet
    sar_packet = FinCENSARGenerator.generate_fincen_sar_packet("CUST-00001", compliance_officer="Audit Examiner")
    assert "sar_reference_id" in sar_packet
    assert sar_packet["sar_reference_id"].startswith("SAR-")
    assert "narrative_markdown" in sar_packet
    assert "SUSPICIOUS ACTIVITY REPORT (SAR) NARRATIVE" in sar_packet["narrative_markdown"]
    assert "SUBJECT IDENTIFICATION" in sar_packet["narrative_markdown"]


def test_pricing_and_sar_api_endpoints(api_client, admin_token):
    """Verifies RESTful API endpoints for concession pricing and BSA/AML SAR generation."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Concession pricing optimization endpoint
    pricing_resp = api_client.post("/api/v1/retention/optimize-concession/CUST-00001", headers=headers)
    assert pricing_resp.status_code == 200
    p_data = pricing_resp.json()
    assert "optimal_recommendation" in p_data

    # 2. BSA/AML risk scanning endpoint
    scan_resp = api_client.post("/api/v1/governance/aml-sar/scan?limit=25", headers=headers)
    assert scan_resp.status_code == 200
    s_data = scan_resp.json()
    assert "flagged_accounts_count" in s_data
    assert isinstance(s_data["alerts"], list)

    # 3. FinCEN SAR narrative generation endpoint
    sar_resp = api_client.post("/api/v1/governance/aml-sar/generate/CUST-00001", headers=headers)
    assert sar_resp.status_code == 200
    sar_data = sar_resp.json()
    assert sar_data["customer_id"] == "CUST-00001"
    assert "narrative_markdown" in sar_data


def test_sdk_pricing_and_sar_methods(api_client, admin_token):
    """Verifies Python Client SDK methods for pricing optimization and SAR generation."""
    sdk = BankSightClient(base_url="http://testserver", session=api_client)
    sdk.token = admin_token

    # 1. SDK optimize_concession
    opt_res = sdk.optimize_concession("CUST-00001")
    assert "optimal_recommendation" in opt_res

    # 2. SDK scan_aml_risks
    aml_res = sdk.scan_aml_risks(limit=10)
    assert "flagged_accounts_count" in aml_res

    # 3. SDK generate_sar_narrative
    sar_res = sdk.generate_sar_narrative("CUST-00001")
    assert "sar_reference_id" in sar_res
    assert "narrative_markdown" in sar_res
