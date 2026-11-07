"""
BankSight Business Reporting & Export Studio
Generates exportable multi-format executive business reports in CSV, styled Excel (.xlsx), and PDF.
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
    BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN
)
from backend.services.reporting_service import ReportingService, REPORT_TYPES

st.set_page_config(page_title="Business Reports | BankSight", page_icon="📑", layout="wide")
apply_banking_theme()

render_page_header(
    title="Executive Business Reporting & Data Export",
    subtitle="Standardized boardroom reports, KPI snapshots, strategic recommendations, and multi-format exports",
    badge_text="Module 10 — Business Reporting"
)

reporting_service = ReportingService()

# Select Report
selected_report = st.selectbox(
    "Select Standard Banking Report:",
    options=REPORT_TYPES,
    index=0
)

# Fetch Report Data
with st.spinner("Compiling report KPIs and executive insights..."):
    report_data = reporting_service.generate_report_data(selected_report)

# Header Meta
st.markdown(
    f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px 24px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0 0 4px 0; color: {BANK_NAVY};">{report_data['title']}</h3>
                <p style="margin: 0; color: #64748B; font-size: 13px;">Generated: {report_data['generation_date']} • Filters: {report_data['applied_filters']}</p>
            </div>
            <div style="font-size: 12px; background: #DEF7EC; color: #03543F; padding: 4px 10px; border-radius: 6px; font-weight: 600;">
                Verified Audit Ready
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Executive Insights
col_sum, col_rec = st.columns(2)
with col_sum:
    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 120px;">
            <div style="font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase;">Executive Analytical Summary</div>
            <p style="font-size: 13px; color: #1E293B; margin: 8px 0 0 0;">{report_data['executive_summary']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_rec:
    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 120px;">
            <div style="font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase;">Strategic Business Recommendations</div>
            <p style="font-size: 13px; color: #1E293B; margin: 8px 0 0 0;">{report_data['recommendations']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# Data Table Preview
st.markdown("##### 📊 **Report Data Preview**")
st.dataframe(report_data["data_table"], use_container_width=True, hide_index=True)

# Multi-Format Export Buttons
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### 📥 **Download Formatted Report**")

e_col1, e_col2, e_col3 = st.columns(3)
safe_filename = selected_report.lower().replace(" ", "_")

with e_col1:
    csv_bytes = reporting_service.export_csv(report_data)
    st.download_button(
        label="📄 Download CSV Format (.csv)",
        data=csv_bytes,
        file_name=f"{safe_filename}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with e_col2:
    xlsx_bytes = reporting_service.export_excel(report_data)
    st.download_button(
        label="📊 Download Excel Format (.xlsx)",
        data=xlsx_bytes,
        file_name=f"{safe_filename}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with e_col3:
    pdf_bytes = reporting_service.export_pdf(report_data)
    st.download_button(
        label="📑 Download PDF Brief (.pdf)",
        data=pdf_bytes,
        file_name=f"{safe_filename}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption(f"Governance Notice: {report_data['data_limitations']}")
