"""
BankSight Enterprise Test Suite: CLV, Uplift Retention & CCAR Stress Testing
Tests discounted Net Present Value formulas, uplift quadrant segmentation,
concession pricing gating, Fed CCAR macroeconomic shocks, and Basel III LCR.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from analytics.clv.uplift_engine import CustomerLifetimeValueEngine
from analytics.stress_testing.ccar_simulator import CCARStressTestSimulator
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


def test_clv_engine_quadrant_segmentation():
    """Verifies DCF calculations and uplift quadrant concession capping logic."""
    # 1. Persuadable Customer
    persuadable = CustomerLifetimeValueEngine.calculate_customer_clv(
        total_balance=120000.0,
        churn_probability=0.45,
        annual_income=95000.0,
        loan_count=1
    )
    assert persuadable["retention_quadrant"] == "Persuadables"
    assert persuadable["clv_36m_npv"] > 1500.0
    assert 0.0 < persuadable["max_allowable_concession_usd"] <= 2500.0

    # 2. Sure Thing (Loyal, high balance, low churn)
    sure_thing = CustomerLifetimeValueEngine.calculate_customer_clv(
        total_balance=150000.0,
        churn_probability=0.02,
        annual_income=110000.0
    )
    assert sure_thing["retention_quadrant"] == "Sure Things"
    assert sure_thing["max_allowable_concession_usd"] == 0.0

    # 3. Lost Cause (High churn > 85%)
    lost_cause = CustomerLifetimeValueEngine.calculate_customer_clv(
        total_balance=100000.0,
        churn_probability=0.92,
        annual_income=70000.0
    )
    assert lost_cause["retention_quadrant"] == "Lost Causes"
    assert lost_cause["max_allowable_concession_usd"] <= 50.0

    # 4. Sleeping Dog (Low balance)
    sleeping_dog = CustomerLifetimeValueEngine.calculate_customer_clv(
        total_balance=250.0,
        churn_probability=0.15,
        annual_income=30000.0
    )
    assert sleeping_dog["retention_quadrant"] == "Sleeping Dogs"
    assert sleeping_dog["max_allowable_concession_usd"] == 0.0


def test_portfolio_clv_aggregation():
    """Verifies fleet-wide CLV aggregation against database."""
    summary = CustomerLifetimeValueEngine.evaluate_portfolio_clv()
    assert "total_customers" in summary
    assert summary["total_customers"] > 0
    assert summary["portfolio_36m_clv_usd"] > 0.0
    assert "Persuadables" in summary["quadrant_distribution"]
    assert "full_dataframe" in summary


def test_ccar_stress_testing_scenarios():
    """Verifies supervisory macroeconomic shocks and Basel III LCR math."""
    # Baseline Scenario
    baseline = CCARStressTestSimulator.run_simulation("BASELINE", custom_hqla_buffer_usd=15000000.0)
    assert baseline["scenario"] == "BASELINE"
    assert baseline["macro_assumptions"]["gdp_growth_pct"] > 0
    assert baseline["basel_iii_liquidity"]["lcr_compliant"] is True

    # Adverse Scenario
    adverse = CCARStressTestSimulator.run_simulation("ADVERSE", custom_hqla_buffer_usd=12000000.0)
    assert adverse["scenario"] == "ADVERSE"
    assert adverse["portfolio_impact"]["stressed_outflow_usd"] > baseline["portfolio_impact"]["stressed_outflow_usd"]

    # Severely Adverse with low HQLA buffer causing deficit
    severely_adverse_low_buffer = CCARStressTestSimulator.run_simulation(
        "SEVERELY_ADVERSE", custom_hqla_buffer_usd=1000000.0
    )
    assert severely_adverse_low_buffer["scenario"] == "SEVERELY_ADVERSE"
    assert severely_adverse_low_buffer["basel_iii_liquidity"]["lcr_compliant"] is False
    assert severely_adverse_low_buffer["basel_iii_liquidity"]["projected_lcr_pct"] < 100.0
    assert "CRITICAL DEFICIT" in severely_adverse_low_buffer["supervisory_recommendation"]

    # All scenarios benchmark
    all_scenarios = CCARStressTestSimulator.run_all_scenarios(hqla_buffer_usd=12000000.0)
    assert len(all_scenarios) == 3
    assert [s["scenario"] for s in all_scenarios] == ["BASELINE", "ADVERSE", "SEVERELY_ADVERSE"]


def test_clv_api_endpoints(api_client, admin_token):
    """Verifies RESTful API endpoints for CLV customer valuation and portfolio summary."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Customer CLV endpoint
    resp = api_client.get("/api/v1/clv/customer/CUST-00001", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["customer_id"] == "CUST-00001"
    assert "clv_36m_npv" in data
    assert "retention_quadrant" in data
    assert "max_allowable_concession_usd" in data

    # 2. Portfolio Summary endpoint
    summary_resp = api_client.get("/api/v1/clv/portfolio-summary", headers=headers)
    assert summary_resp.status_code == 200
    s_data = summary_resp.json()
    assert "portfolio_36m_clv_usd" in s_data
    assert "clv_at_risk_usd" in s_data
    assert "quadrant_distribution" in s_data


def test_stress_test_governance_api(api_client, admin_token):
    """Verifies RESTful API endpoints for Fed CCAR stress testing simulations."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Run single simulation
    sim_payload = {"scenario": "ADVERSE", "hqla_buffer_usd": 14000000.0}
    resp = api_client.post("/api/v1/governance/stress-test/simulate", json=sim_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario"] == "ADVERSE"
    assert "basel_iii_liquidity" in data

    # 2. Run multi-scenario benchmark
    bench_resp = api_client.get("/api/v1/governance/stress-test/benchmark?hqla_buffer_usd=12000000.0", headers=headers)
    assert bench_resp.status_code == 200
    bench_data = bench_resp.json()
    assert len(bench_data) == 3


def test_sdk_clv_and_stress_testing_methods(api_client, admin_token):
    """Verifies SDK client methods for CLV and Stress Testing."""
    sdk = BankSightClient(base_url="http://testserver", session=api_client)
    sdk.token = admin_token

    # 1. SDK get_customer_clv
    clv_res = sdk.get_customer_clv("CUST-00001")
    assert clv_res["customer_id"] == "CUST-00001"
    assert "clv_36m_npv" in clv_res

    # 2. SDK get_portfolio_clv_summary
    port_res = sdk.get_portfolio_clv_summary()
    assert port_res["portfolio_36m_clv_usd"] > 0

    # 3. SDK simulate_stress_test
    sim_res = sdk.simulate_stress_test("BASELINE", hqla_buffer_usd=15000000.0)
    assert sim_res["scenario"] == "BASELINE"

    # 4. SDK benchmark_stress_testing
    bench_res = sdk.benchmark_stress_testing(hqla_buffer_usd=10000000.0)
    assert len(bench_res) == 3
