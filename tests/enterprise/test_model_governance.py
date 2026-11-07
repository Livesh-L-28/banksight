"""
Enterprise Model Risk Management Tests (SR 11-7 & Bias Auditing)
"""

import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from analytics.governance.sr11_7_validator import SR117Validator


def test_psi_drift_calculation():
    """Validates Population Stability Index correctly flags stable vs drifted distributions."""
    np.random.seed(42)
    # Identical distributions should have near-zero PSI
    baseline = np.random.uniform(0.1, 0.9, 1000)
    comparison_stable = np.random.uniform(0.1, 0.9, 1000)

    psi_stable = SR117Validator.calculate_psi(comparison_stable, baseline)
    assert psi_stable < 0.10, f"Expected stable PSI < 0.10, got {psi_stable}"

    # Significantly shifted distribution should have high PSI
    comparison_drifted = np.random.beta(5, 1, 1000)
    psi_drifted = SR117Validator.calculate_psi(comparison_drifted, baseline)
    assert psi_drifted > 0.25, f"Expected drifted PSI > 0.25, got {psi_drifted}"


def test_disparate_impact_auditing():
    """Validates Fair Lending Disparate Impact Ratio (DIR) compliance checks."""
    data = {
        "gender": ["M"] * 500 + ["F"] * 500,
        "churn_flag": [1] * 100 + [0] * 400 + [1] * 95 + [0] * 405
    }
    df = pd.DataFrame(data)

    audit = SR117Validator.audit_disparate_impact(df, "gender", privileged_val="M")
    assert audit["compliant_with_four_fifths_rule"] is True
    assert 0.80 <= audit["disparate_impact_ratio"] <= 1.25


def test_full_sr11_7_validation_pipeline():
    """Validates end-to-end SR 11-7 audit and markdown dossier generation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        validator = SR117Validator(output_dir=Path(tmp_dir))

        benchmark_metrics = {
            "LogisticRegression": {"precision": 0.81, "recall": 0.75, "roc_auc": 0.85},
            "GradientBoosting": {"precision": 0.89, "recall": 0.84, "roc_auc": 0.93}
        }

        test_data = {
            "age": [25, 45, 60, 32, 55, 68] * 20,
            "gender": ["M", "F", "F", "M", "M", "F"] * 20,
            "churn_flag": [0, 1, 0, 0, 1, 0] * 20,
            "churn_probability": [0.15, 0.82, 0.35, 0.12, 0.77, 0.40] * 20
        }
        df = pd.DataFrame(test_data)

        audit_results = validator.run_full_validation_audit(benchmark_metrics, df)
        assert audit_results["overall_assessment"] == "APPROVED_FOR_PRODUCTION_USE"

        # Verify markdown report created
        report_file = Path(tmp_dir) / "SR_11_7_Model_Validation_Report.md"
        assert report_file.exists()
        content = report_file.read_text(encoding="utf-8")
        assert "Federal Reserve SR 11-7" in content
        assert "Champion Model Selection" in content


def test_regulatory_board_report_api():
    """Validates generation of formal board report in JSON, Markdown, and HTML via API."""
    from fastapi.testclient import TestClient
    from backend.api.main import app

    client = TestClient(app)

    # 1. Login as Admin
    login_resp = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. JSON Format
    resp_json = client.get("/api/v1/governance/board-report?format=json", headers=headers)
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert "report_id" in data
    assert "executive_kpis" in data
    assert "model_governance" in data
    assert data["model_governance"]["standard"] == "Federal Reserve SR 11-7 / OCC 2011-12"

    # 3. Markdown Format
    resp_md = client.get("/api/v1/governance/board-report?format=markdown", headers=headers)
    assert resp_md.status_code == 200
    assert "BankSight Institutional Board & Regulatory Oversight Packet" in resp_md.text

    # 4. HTML Format
    resp_html = client.get("/api/v1/governance/board-report?format=html", headers=headers)
    assert resp_html.status_code == 200
    assert "<!DOCTYPE html>" in resp_html.text
    assert "BankSight Executive Board & Regulatory Oversight Report" in resp_html.text

