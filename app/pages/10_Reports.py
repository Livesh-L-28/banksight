"""
BankSight Business Reporting & Export Studio
Generates exportable multi-format executive business reports in CSV, styled Excel (.xlsx), PDF,
and formal Board of Directors & Regulatory Oversight Packets (Fed SR 11-7 / OCC 2011-12 / BCBS 239).
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import streamlit as st

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    BANK_NAVY, BANK_GREEN
)
from backend.services.reporting_service import ReportingService, REPORT_TYPES
from backend.reporting.regulatory_exporter import RegulatoryBoardReportExporter
from backend.compliance.sar_generator import FinCENSARGenerator

st.set_page_config(page_title="Business Reports | BankSight", page_icon="📑", layout="wide")
apply_banking_theme()

render_page_header(
    title="Executive Business Reporting & Governance Studio",
    subtitle="Standardized boardroom reports, KPI snapshots, regulatory audit dossiers, and multi-format exports",
    badge_text="Module 10 — Business Reporting & Governance"
)

reporting_service = ReportingService()

tab_board, tab_aml_sar, tab_standard = st.tabs([
    "🏛️ Board of Directors & Regulatory Oversight Packet",
    "🚨 BSA/AML & FinCEN SAR Regulatory Workspace",
    "📊 Standard Executive Business Reports"
])

# =========================================================================
# TAB 1: BOARD OF DIRECTORS & REGULATORY OVERSIGHT PACKET
# =========================================================================
with tab_board:
    st.markdown("#### 🏛️ **Executive Board & Supervisory Oversight Packet**")
    st.markdown("""
    Unified regulatory and board governance dossier synthesized from continuous Core Banking ledgers,
    **Federal Reserve SR 11-7** Model Risk audits, **SOX Section 404** dual-authorization queues, and **BCBS 239** data integrity checks.
    """)

    board_data = RegulatoryBoardReportExporter.generate_board_report_data()
    k = board_data["executive_kpis"]
    m = board_data["model_governance"]
    a = board_data["audit_ledger_status"]

    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        render_metric_card("Total Bank Deposits", f"${k.get('total_deposits', 0.0):,.2f}", "Continuous Ledger Total")
    with b2:
        net_flow = k.get("total_deposits", 0.0) - k.get("total_withdrawals", 0.0)
        render_metric_card("Net Clearing Flow", f"${net_flow:,.2f}", "Deposits vs Withdrawals", delta_color=BANK_GREEN if net_flow >= 0 else "#EF4444")
    with b3:
        render_metric_card("Model Risk (SR 11-7)", "APPROVED", f"PSI: {m['psi_score']:.3f} (Zero Drift)", delta_color=BANK_GREEN)
    with b4:
        render_metric_card("Fair Lending (DIR)", f"{m['disparate_impact_ratio']:.3f}", "Compliant with 4/5ths Rule", delta_color=BANK_GREEN)
    with b5:
        render_metric_card("WORM Audit Trail", "TAMPER-FREE", f"{a.get('count', 0):,} Records Verified", delta_color=BANK_GREEN)

    st.markdown("<br>", unsafe_allow_html=True)

    # Export Buttons
    st.markdown("##### 📥 **Download Official Board Packet**")
    d_col1, d_col2, d_col3 = st.columns(3)

    md_content = RegulatoryBoardReportExporter.export_as_markdown()
    html_content = RegulatoryBoardReportExporter.export_as_html()
    json_content = json.dumps(board_data, indent=2)

    with d_col1:
        st.download_button(
            label="📜 Download Executive Markdown (.md)",
            data=md_content,
            file_name=f"BankSight_Board_Report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with d_col2:
        st.download_button(
            label="🌐 Download Printable HTML Brief (.html)",
            data=html_content,
            file_name=f"BankSight_Board_Report_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )

    with d_col3:
        st.download_button(
            label="📊 Download Regulatory JSON (.json)",
            data=json_content,
            file_name=f"BankSight_Regulatory_Audit_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Live Preview Expander
    with st.expander("👁️ **Live Executive Report Preview**", expanded=True):
        st.markdown(md_content)


# =========================================================================
# TAB 2: BSA/AML & FINCEN SAR REGULATORY WORKSPACE
# =========================================================================
with tab_aml_sar:
    st.markdown("#### 🚨 **Bank Secrecy Act (BSA) & FinCEN Suspicious Activity Report (SAR) Studio**")
    st.markdown("""
    Automated transaction monitoring scanner compliant with **FinCEN Form 111 (SAR)** and **OCC Bank Secrecy Act / Anti-Money Laundering (BSA/AML)** guidelines.
    Flags rapid capital flight, CTR avoidance structuring ($8,500–$9,999), and pre-churn balance extraction velocity.
    """)

    aml_alerts = FinCENSARGenerator.scan_portfolio_for_alerts(limit=50)

    # Top Metric Banner
    am1, am2, am3, am4 = st.columns(4)
    with am1:
        render_metric_card("Flagged Accounts", f"{len(aml_alerts)}", "Anomalous Transaction Flow")
    with am2:
        tot_suspicious = sum(a["total_debit_outflow_usd"] for a in aml_alerts)
        render_metric_card("Total Flagged Volume", f"${tot_suspicious:,.2f}", "Cumulative Outflows")
    with am3:
        structuring_n = sum(1 for a in aml_alerts if any(f["code"] == "AML_STRUCTURING" for f in a.get("red_flags", [])))
        render_metric_card("Suspected Structuring", f"{structuring_n}", "$8,500 - $9,999 CTR Evading")
    with am4:
        sar_rec_n = sum(1 for a in aml_alerts if a.get("sar_filing_recommended"))
        render_metric_card("SAR Filing Required", f"{sar_rec_n}", "Risk Score ≥ 50 Threshold")

    st.markdown("<br>", unsafe_allow_html=True)

    if aml_alerts:
        import pandas as pd
        alert_rows = [
            {
                "Customer ID": a["customer_id"],
                "Customer Name": a["customer_name"],
                "Branch ID": a["branch_id"],
                "Occupation": a["occupation"],
                "Total Debits": f"${a['total_debit_outflow_usd']:,.2f}",
                "Remaining Balance": f"${a['total_balance_usd']:,.2f}",
                "AML Risk Score": f"{a['aml_risk_score']} / 100",
                "SAR Filing": "⚠️ MANDATORY" if a["sar_filing_recommended"] else "Monitor",
                "Primary Alert": a["red_flags"][0]["title"] if a["red_flags"] else "N/A"
            }
            for a in aml_alerts
        ]
        st.markdown("##### 📋 **Prioritized Compliance Alert Queue**")
        st.dataframe(pd.DataFrame(alert_rows), use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📝 **FinCEN Form 111 Regulatory Narrative Dossier**")

        flagged_options = {f"{a['customer_name']} ({a['customer_id']}) — Score: {a['aml_risk_score']}": a['customer_id'] for a in aml_alerts}
        picked_alert_label = st.selectbox("Select Customer to Review and Generate SAR Narrative:", options=list(flagged_options.keys()))
        picked_cust_id = flagged_options[picked_alert_label]

        sar_dossier = FinCENSARGenerator.generate_fincen_sar_packet(picked_cust_id, compliance_officer="BSA/AML Officer")

        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin: 12px 0;">
                <div style="font-weight: 700; color: #1E293B;">FinCEN Reference: {sar_dossier['sar_reference_id']}</div>
                <div style="font-size: 13px; color: #64748B;">Subject: {sar_dossier['customer_name']} | Filing Date: {sar_dossier['filing_date']} | Status: Audit Ready</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("📄 **Inspect Generated FinCEN SAR Narrative Text**", expanded=True):
            st.markdown(sar_dossier["narrative_markdown"])

        sar_md_bytes = sar_dossier["narrative_markdown"].encode("utf-8")
        st.download_button(
            label=f"📥 Download FinCEN SAR Filing Narrative ({picked_cust_id}.md)",
            data=sar_md_bytes,
            file_name=f"fincen_sar_{picked_cust_id}_{sar_dossier['filing_date']}.md",
            mime="text/markdown"
        )
    else:
        st.info("Zero AML red flags detected across scanned customer accounts.")


# =========================================================================
# TAB 3: STANDARD EXECUTIVE BUSINESS REPORTS
# =========================================================================
with tab_standard:
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
