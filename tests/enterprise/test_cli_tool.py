"""
BankSight Enterprise Test Suite: Institutional CLI Utility
Tests all command-line operations (--kpis, --predict, --clv, --stress-test, --scan-aml, --sar, --verify-audit).
"""

import subprocess
import sys


def run_cli_command(*args):
    cmd = [sys.executable, "scripts/banksight_cli.py", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def test_cli_kpis():
    res = run_cli_command("--kpis")
    assert res.returncode == 0
    assert "Total Depository Customers" in res.stdout
    assert "Annualized Churn Rate" in res.stdout


def test_cli_predict():
    res = run_cli_command("--predict", "CUST-00001")
    assert res.returncode == 0
    assert "Risk Tier:" in res.stdout
    assert "Churn Score:" in res.stdout


def test_cli_clv():
    res = run_cli_command("--clv", "CUST-00001")
    assert res.returncode == 0
    assert "36-Month Discounted CLV:" in res.stdout
    assert "Uplift Retention Quadrant:" in res.stdout


def test_cli_optimize_concession():
    res = run_cli_command("--optimize-concession", "CUST-00001")
    assert res.returncode == 0
    assert "RECOMMENDED OPTIMAL OFFER:" in res.stdout
    assert "Expected Net Value Added:" in res.stdout


def test_cli_stress_test():
    res = run_cli_command("--stress-test", "ADVERSE", "--hqla", "12000000")
    assert res.returncode == 0
    assert "SUPERVISORY SCENARIO:" in res.stdout
    assert "Projected Basel III LCR:" in res.stdout


def test_cli_scan_aml():
    res = run_cli_command("--scan-aml")
    assert res.returncode == 0
    assert "Scanned accounts" in res.stdout


def test_cli_sar():
    res = run_cli_command("--sar", "CUST-00001")
    assert res.returncode == 0
    assert "SUSPICIOUS ACTIVITY REPORT (SAR) NARRATIVE" in res.stdout


def test_cli_verify_audit():
    res = run_cli_command("--verify-audit")
    assert res.returncode == 0
    assert "Chain Integrity Status: VALID" in res.stdout


def test_cli_export_board_report(tmp_path):
    report_file = tmp_path / "board_report_test.md"
    res = run_cli_command("--export-board-report", str(report_file))
    assert res.returncode == 0
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "BOARD OF DIRECTORS" in content
