"""
End-to-End Smoke Tests for BankSight Streamlit Application Modules
"""

import pytest
import subprocess
import sys


def test_app_pages_syntax_compilation():
    """Verifies all application files compile without syntax errors."""
    files = [
        "app/Home.py",
        "app/components/ui_components.py",
        "app/pages/01_Overview.py",
        "app/pages/02_Customer_360.py",
        "app/pages/03_Segmentation.py",
        "app/pages/04_Churn_Intelligence.py",
        "app/pages/05_Retention_Management.py",
        "app/pages/06_Transaction_Analytics.py",
        "app/pages/07_Campaign_Intelligence.py",
        "app/pages/08_Branch_Analytics.py",
        "app/pages/09_Product_Intelligence.py",
        "app/pages/10_Reports.py",
        "app/pages/11_Data_Management.py",
        "app/pages/12_Model_Management.py",
        "app/pages/13_Settings.py"
    ]
    for file_path in files:
        res = subprocess.run([sys.executable, "-m", "py_compile", file_path], capture_output=True, text=True)
        assert res.returncode == 0, f"Failed compilation on {file_path}: {res.stderr}"

