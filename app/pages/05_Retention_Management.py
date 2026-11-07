"""
BankSight Operational Retention Management System
Closed-loop retention case management: RM assignment, status transitions, offer tracking, and persistent audit logs.
"""

import sys
from pathlib import Path
from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    format_currency, get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN, BANK_RED
)
from backend.services.retention_service import RetentionService
from backend.services.branch_service import BranchService
from backend.database.connection import get_db_session
from backend.models import RelationshipManager

st.set_page_config(page_title="Retention Management | BankSight", page_icon="🛡️", layout="wide")
apply_banking_theme()

render_page_header(
    title="Operational Retention Management System",
    subtitle="Proactive at-risk case workflows, RM assignment, tailored retention incentives, and auditable status tracking",
    badge_text="Module 5 — Retention Ops"
)

retention_service = RetentionService()

# Funnel Summary Metrics
funnel_data = retention_service.get_funnel_analytics()
counts = funnel_data["funnel_counts"]

f1, f2, f3, f4, f5 = st.columns(5)
with f1:
    render_metric_card("Total Enrolled Cases", f"{funnel_data['total_cases']:,}", "At-Risk Account Queue")
with f2:
    render_metric_card("In Progress / Outreach", f"{counts['Assigned'] + counts['Contacted'] + counts['Offer Proposed']:,}", "Active Interventions")
with f3:
    render_metric_card("Confirmed Retained", f"{counts['Retained']:,}", "Saved Banking Customers", delta_color=BANK_GREEN)
with f4:
    render_metric_card("Not Retained / Lost", f"{counts['Not Retained']:,}", "Defected Accounts", delta_color=BANK_RED)
with f5:
    render_metric_card("Retention Conversion", f"{funnel_data['retention_conversion_rate']:.1f}%", "Outreach Success Rate")

st.markdown("<br>", unsafe_allow_html=True)

# Visual Funnel
st.markdown("##### 📊 **Retention Lifecycle Funnel**")
funnel_df = pd.DataFrame([
    {"Stage": "1. Identified", "Cases": counts["Identified"]},
    {"Stage": "2. Assigned", "Cases": counts["Assigned"]},
    {"Stage": "3. Contacted", "Cases": counts["Contacted"]},
    {"Stage": "4. Offer Proposed", "Cases": counts["Offer Proposed"]},
    {"Stage": "5. Retained", "Cases": counts["Retained"]},
])
fig_funnel = px.funnel(funnel_df, x="Cases", y="Stage", color="Stage", color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731", BANK_GREEN])
fig_funnel.update_layout(**get_banking_chart_layout("Operational Retention Funnel Progression", height=280))
st.plotly_chart(fig_funnel, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Cases Table & Management Workspace
col_table, col_form = st.columns([3, 2])

with col_table:
    st.markdown("##### 📋 **Active Retention Cases Queue**")

    q_col1, q_col2 = st.columns(2)
    with q_col1:
        status_sel = st.selectbox(
            "Filter Status:",
            options=["All", "Identified", "Assigned", "Contacted", "Offer Proposed", "Retained", "Not Retained", "Closed"],
            index=0
        )
    with q_col2:
        risk_sel = st.selectbox(
            "Filter Risk Tier:",
            options=["All", "High Risk", "Medium Risk", "Low Risk"],
            index=0
        )

    cases = retention_service.get_cases(
        status_filter=status_sel if status_sel != "All" else None,
        risk_filter=risk_sel if risk_sel != "All" else None
    )

    if cases:
        cases_df = pd.DataFrame(cases)[[
            "case_id", "customer_id", "customer_name", "churn_probability",
            "status", "proposed_offer", "rm_name"
        ]]
        st.dataframe(
            cases_df.rename(columns={
                "case_id": "Case ID",
                "customer_id": "Cust ID",
                "customer_name": "Customer Name",
                "churn_probability": "Churn Prob",
                "status": "Current Status",
                "proposed_offer": "Proposed Offer",
                "rm_name": "Assigned RM"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No retention cases matching filter criteria.")

with col_form:
    st.markdown("##### ⚙️ **Update Retention Case & Log Touchpoint**")
    if cases:
        case_options = {f"{c['case_id']} — {c['customer_name']} ({c['status']})": c["case_id"] for c in cases}
        selected_case_label = st.selectbox("Select Case to Manage:", options=list(case_options.keys()))
        target_case_id = case_options[selected_case_label]
        target_case = next(c for c in cases if c["case_id"] == target_case_id)

        # Get list of relationship managers
        session = get_db_session()
        rms = session.query(RelationshipManager).filter(RelationshipManager.is_active).all()
        rm_map = {f"{rm.first_name} {rm.last_name} ({rm.rm_id})": rm.rm_id for rm in rms}
        session.close()

        with st.form("retention_action_form"):
            st.markdown(f"**Customer:** {target_case['customer_name']} (`{target_case['customer_id']}`)")
            st.markdown(f"**Churn Risk:** `{target_case['churn_probability']:.1%}` — Reason: *{target_case['churn_reason']}*")

            new_status_val = st.selectbox(
                "Advance Status to:",
                options=["Identified", "Assigned", "Contacted", "Offer Proposed", "Retained", "Not Retained", "Closed"],
                index=["Identified", "Assigned", "Contacted", "Offer Proposed", "Retained", "Not Retained", "Closed"].index(target_case["status"])
            )

            assigned_rm_label = st.selectbox("Assign / Reassign RM:", options=list(rm_map.keys()))
            selected_rm_id = rm_map[assigned_rm_label]

            offer_val = st.selectbox(
                "Select Retention Incentive Offer:",
                options=[
                    "None / Inactive",
                    "3-Month Account Maintenance Fee Waiver ($36 Value)",
                    "High-Yield CD Match (+0.40% APY Boost)",
                    "Dedicated Private Banker & Priority Concierge",
                    "Waived Foreign Transaction Fees on Debit Card",
                    "Custom Courtesy Credit ($50 goodwill refund)"
                ],
                index=0
            )

            notes_val = st.text_area("RM Consultation Notes:", placeholder="Summarize client interaction, satisfaction, and response...")
            action_user = st.text_input("Officer Name:", value="RM Sarah Jenkins")

            submit_action = st.form_submit_button("💾 Save & Persist Retention Update")

            if submit_action:
                retention_service.assign_relationship_manager(
                    case_id=target_case_id,
                    rm_id=selected_rm_id,
                    performed_by=action_user,
                    notes=f"Assigned to {assigned_rm_label}"
                )
                retention_service.update_case(
                    case_id=target_case_id,
                    new_status=new_status_val,
                    performed_by=action_user,
                    notes=notes_val or "Status transitioned via operational console.",
                    proposed_offer=offer_val if offer_val != "None / Inactive" else None
                )
                st.success(f"Case {target_case_id} updated successfully to status: {new_status_val}")
                st.rerun()

        # Action Audit History
        st.markdown("###### 📜 **Case Action History**")
        history = retention_service.get_case_action_history(target_case_id)
        if history:
            for act in history[:5]:
                st.markdown(
                    f"""
                    <div style="font-size: 12px; border-left: 2px solid {BANK_BLUE}; padding-left: 8px; margin-bottom: 8px;">
                        <strong>{act['action_type']}</strong> by {act['performed_by']} ({act['timestamp'][:16]})<br>
                        <span style="color: #64748B;">{act['notes']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("Select or filter cases to manage.")
