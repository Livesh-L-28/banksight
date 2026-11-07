"""
BankSight Data Management & Quality Control Studio
File ingestion, schema validation, data quality audit logs, and rejected-record tracking.
"""

import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN, BANK_RED
)
from data_pipeline.pipeline_manager import PipelineManager
from backend.database.connection import get_db_session
from backend.models import DataQualityResult, DataImportJob

st.set_page_config(page_title="Data Management | BankSight", page_icon="🗄️", layout="wide")
apply_banking_theme()

render_page_header(
    title="Data Management & Quality Governance",
    subtitle="Automated file ingestion, schema validation, duplicate detection, rejected-record isolation, and audit logs",
    badge_text="Module 11 — Data Pipeline"
)

pipeline_mgr = PipelineManager()

# Top Metrics Row
session = get_db_session()
dq_records = session.query(DataQualityResult).order_by(DataQualityResult.executed_at.desc()).all()
session.close()

total_audits = len(dq_records)
passed_audits = sum(1 for d in dq_records if d.status == "Passed")
failed_audits = sum(1 for d in dq_records if d.status == "Failed")

m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Total Quality Audits", f"{total_audits}", "Execution Runs")
with m2:
    render_metric_card("Passed Checks", f"{passed_audits}", "Zero Schema Violations", delta_color=BANK_GREEN)
with m3:
    render_metric_card("Failed / Quarantined", f"{failed_audits}", "Rejections Isolated", delta_color=BANK_RED if failed_audits > 0 else BANK_GREEN)
with m4:
    render_metric_card("Quality Conformance", f"{(passed_audits / max(total_audits, 1)) * 100:.1f}%", "Domain Conformance")

st.markdown("<br>", unsafe_allow_html=True)

# Ingestion Upload Workspace
st.markdown("##### 📤 **Ingest New Tabular Banking File**")
st.caption("Supported formats: CSV, XLSX (Max 25MB). All uploads undergo schema, boundary, and referential validation.")

u_col1, u_col2 = st.columns([2, 1])
with u_col1:
    uploaded_file = st.file_uploader("Choose a Customer or Transaction File", type=["csv", "xlsx"])
with u_col2:
    file_type = st.selectbox("File Entity Type:", options=["Customers Dataset", "Transactions Dataset"])

if uploaded_file is not None:
    temp_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / uploaded_file.name

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File uploaded successfully: `{uploaded_file.name}` ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("🚀 Process & Validate Ingestion Pipeline"):
        with st.spinner("Executing schema validation, range checks, and deduplication..."):
            if "Customer" in file_type:
                res = pipeline_mgr.run_customer_pipeline(temp_path)
            else:
                res = pipeline_mgr.run_transaction_pipeline(temp_path)

        st.success(
            f"Pipeline complete! Processed {res['total_records']} rows: "
            f"{res['valid_records']} valid, {res['rejected_records']} rejected."
        )

st.markdown("<br>", unsafe_allow_html=True)

# Data Quality Audit Logs Table
st.markdown("##### 📜 **Data Quality Execution Audit Trail**")
if dq_records:
    log_rows = [
        {
            "Check ID": r.check_id,
            "Check Name": r.check_name,
            "Target Table": r.target_table,
            "Total Evaluated": r.total_evaluated,
            "Failed Count": r.failed_count,
            "Failure Rate (%)": f"{r.failure_rate_pct:.2f}%",
            "Audit Status": r.status,
            "Execution Timestamp": r.executed_at.strftime("%Y-%m-%d %H:%M:%S") if r.executed_at else "N/A"
        }
        for r in dq_records[:20]
    ]
    st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)
else:
    st.info("No prior data quality check logs recorded.")
