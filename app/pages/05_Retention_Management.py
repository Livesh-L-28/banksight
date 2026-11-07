"""
BankSight Operational Retention Management System
Closed-loop retention case management: RM assignment, status transitions, offer tracking,
SOX 404 Four-Eyes Dual-Authorization, and real-time streaming attrition triggers.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
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
from backend.streaming.event_processor import stream_processor
from backend.streaming.event_schemas import LargeWithdrawalEvent, ComplaintLoggedEvent
from backend.database.connection import get_db_session
from backend.models import RelationshipManager, Customer

st.set_page_config(page_title="Retention Management | BankSight", page_icon="🛡️", layout="wide")
apply_banking_theme()

render_page_header(
    title="Operational Retention Management System",
    subtitle="Proactive at-risk case workflows, RM assignment, SOX 404 dual-authorization, and real-time streaming triggers",
    badge_text="Module 5 — Retention Ops & Governance"
)

retention_service = RetentionService()

# Funnel Summary Metrics
funnel_data = retention_service.get_funnel_analytics()
counts = funnel_data["funnel_counts"]

# Check pending approval count
pending_cases = retention_service.get_cases(status_filter="Pending Approval")
pending_count = len(pending_cases)

f1, f2, f3, f4, f5 = st.columns(5)
with f1:
    render_metric_card("Total Enrolled Cases", f"{funnel_data['total_cases']:,}", "At-Risk Account Queue")
with f2:
    render_metric_card("In Progress / Outreach", f"{counts['Assigned'] + counts['Contacted'] + counts['Offer Proposed']:,}", "Active Interventions")
with f3:
    render_metric_card("Pending Dual-Auth", f"{pending_count:,}", "SOX 404 Manager Queue", delta_color=BANK_ACCENT if pending_count > 0 else "#64748B")
with f4:
    render_metric_card("Confirmed Retained", f"{counts['Retained']:,}", "Saved Banking Customers", delta_color=BANK_GREEN)
with f5:
    render_metric_card("Retention Conversion", f"{funnel_data['retention_conversion_rate']:.1f}%", "Outreach Success Rate")

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab_cases, tab_four_eyes, tab_streaming = st.tabs([
    "📋 Case Queue & Workflow",
    f"🏛️ Senior Manager Dual-Authorization Queue ({pending_count})",
    "⚡ Real-Time Streaming & Capital Flight Monitor"
])

# =========================================================================
# TAB 1: CASE QUEUE & WORKFLOW
# =========================================================================
with tab_cases:
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
    fig_funnel.update_layout(**get_banking_chart_layout("Operational Retention Funnel Progression", height=260))
    st.plotly_chart(fig_funnel, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_table, col_form = st.columns([3, 2])

    with col_table:
        st.markdown("##### 📋 **Active Retention Cases Queue**")

        q_col1, q_col2 = st.columns(2)
        with q_col1:
            status_sel = st.selectbox(
                "Filter Status:",
                options=["All", "Identified", "Assigned", "Contacted", "Offer Proposed", "Pending Approval", "Retained", "Not Retained", "Closed"],
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
        st.markdown("##### ⚙️ **Update Retention Case & Propose Offer**")
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

            # Algorithmic Concession Pricing Optimization
            from analytics.retention.pricing_optimizer import ConcessionPricingOptimizer
            pricing_rec = ConcessionPricingOptimizer.optimize_for_customer_id(target_case["customer_id"])
            if "optimal_recommendation" in pricing_rec:
                opt_rec = pricing_rec["optimal_recommendation"]
                prof_rec = pricing_rec["customer_profile"]
                with st.expander("🤖 **AI Concession Pricing Recommendation**", expanded=True):
                    st.markdown(
                        f"""
                        <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #20BF6B; border-radius: 6px; padding: 12px; margin-bottom: 8px;">
                            <div style="font-weight: 700; color: #1E293B; font-size: 14px;">🎯 Recommended: {opt_rec['offer_name']}</div>
                            <div style="font-size: 13px; color: #475569; margin-top: 4px;">
                                <strong>Expected Net Gain:</strong> ${opt_rec['expected_net_gain_usd']:,.2f} &nbsp;|&nbsp;
                                <strong>Projected Retention:</strong> {opt_rec['projected_retention_probability']:.1%} &nbsp;|&nbsp;
                                <strong>Allowable Cap:</strong> ${prof_rec['max_allowable_concession_usd']:,.2f} ({prof_rec['retention_quadrant']})
                            </div>
                            <div style="font-size: 12px; color: #64748B; margin-top: 4px;"><em>{opt_rec['rationale']}</em></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            with st.form("retention_action_form"):
                st.markdown(f"**Customer:** {target_case['customer_name']} (`{target_case['customer_id']}`)")
                st.markdown(f"**Churn Risk:** `{target_case['churn_probability']:.1%}` — Reason: *{target_case['churn_reason']}*")

                status_list = ["Identified", "Assigned", "Contacted", "Offer Proposed", "Pending Approval", "Retained", "Not Retained", "Closed"]
                cur_status_idx = status_list.index(target_case["status"]) if target_case["status"] in status_list else 0
                new_status_val = st.selectbox("Advance Status to:", options=status_list, index=cur_status_idx)

                assigned_rm_label = st.selectbox("Assign / Reassign RM:", options=list(rm_map.keys()))
                selected_rm_id = rm_map[assigned_rm_label]

                offer_val = st.selectbox(
                    "Select Retention Incentive Package:",
                    options=[
                        "None / Inactive",
                        "3-Month Account Maintenance Fee Waiver ($36 Value)",
                        "High-Yield CD Match (+0.40% APY Boost)",
                        "Dedicated Private Banker & Priority Concierge",
                        "Waived Foreign Transaction Fees on Debit Card",
                        "Custom Courtesy Credit ($50 goodwill refund)",
                        "Special Tier-1 Deposit Incentive (> $500 concession)"
                    ],
                    index=0
                )

                st.markdown("###### 💵 **Financial Concession Values (SOX 404 Thresholds)**")
                fc1, fc2 = st.columns(2)
                with fc1:
                    concession_usd = st.number_input("Concession Value ($ USD):", min_value=0.0, max_value=25000.0, value=0.0, step=50.0)
                with fc2:
                    concession_bps = st.number_input("Rate Adjustment (Basis Points):", min_value=0, max_value=500, value=0, step=10)

                if concession_usd > 500.0 or concession_bps > 50:
                    st.warning("⚠️ **Notice:** Concessions exceeding **$500.00** or **50 bps** mandate SOX 404 Dual Authorization. Submitting will place this case in **Pending Approval**.")

                notes_val = st.text_area("RM Consultation Notes:", placeholder="Summarize client interaction, satisfaction, and response...")
                action_user = st.text_input("Officer Name:", value="RM Sarah Jenkins")

                submit_action = st.form_submit_button("💾 Save & Persist Retention Update")

                if submit_action:
                    # Update RM assignment first
                    retention_service.assign_relationship_manager(
                        case_id=target_case_id,
                        rm_id=selected_rm_id,
                        performed_by=action_user,
                        notes=f"Assigned to {assigned_rm_label}"
                    )

                    # If concession exceeds threshold, route to dual authorization
                    if concession_usd > 500.0 or concession_bps > 50:
                        res = retention_service.submit_concession_offer(
                            case_id=target_case_id,
                            rm_name=action_user,
                            rm_id=selected_rm_id,
                            offer_name=offer_val,
                            financial_concession_value=concession_usd,
                            rate_adjustment_bps=concession_bps,
                            notes=notes_val or "High-value concession submitted for Senior Manager approval."
                        )
                        st.info(f"🏛️ Concession submitted! Held in **Pending Approval** per SOX 404 policy. Case ID: {target_case_id}")
                    else:
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

# =========================================================================
# TAB 2: SOX 404 DUAL-AUTHORIZATION QUEUE
# =========================================================================
with tab_four_eyes:
    st.markdown("#### 🏛️ **Senior Manager Dual-Authorization Queue**")
    st.markdown("""
    Under **Sarbanes-Oxley (SOX) Section 404** and internal bank risk governance controls, any customer retention concession
    exceeding **$500.00** in direct financial value or **50 basis points** in interest rate adjustment requires independent review
    and dual authorization by an authorized Branch Manager, Executive, or Risk Officer. Strict **Segregation of Duties** applies:
    the reviewing manager cannot be the submitting Relationship Manager.
    """)

    if not pending_cases:
        st.success("✅ **Queue Cleared:** There are currently zero retention concessions awaiting dual-authorization review.")
    else:
        st.warning(f"⚠️ **Action Required:** {len(pending_cases)} high-value retention concession(s) awaiting Senior Manager authorization.")

        p_col_left, p_col_right = st.columns([3, 2])

        with p_col_left:
            st.markdown("##### 📥 **Pending Concession Requests**")
            pending_df = pd.DataFrame(pending_cases)[[
                "case_id", "customer_id", "customer_name", "churn_probability", "proposed_offer", "rm_name"
            ]]
            st.dataframe(
                pending_df.rename(columns={
                    "case_id": "Case ID",
                    "customer_id": "Cust ID",
                    "customer_name": "Customer Name",
                    "churn_probability": "Churn Risk",
                    "proposed_offer": "Proposed Concession & Terms",
                    "rm_name": "Submitting RM"
                }),
                use_container_width=True,
                hide_index=True
            )

        with p_col_right:
            st.markdown("##### ⚖️ **Adjudicate Concession Request**")
            p_case_options = {f"{c['case_id']} — {c['customer_name']}": c["case_id"] for c in pending_cases}
            sel_p_label = st.selectbox("Select Concession to Review:", options=list(p_case_options.keys()))
            target_p_id = p_case_options[sel_p_label]
            target_p = next(c for c in pending_cases if c["case_id"] == target_p_id)

            st.info(f"**Customer:** {target_p['customer_name']} (`{target_p['customer_id']}`)\n\n"
                    f"**Proposed Concession:** {target_p['proposed_offer']}\n\n"
                    f"**Submitting RM:** {target_p['rm_name']}")

            with st.form("dual_authorization_form"):
                approver_role = st.selectbox("Authorizing Role:", ["BranchManager", "Executive", "Admin"])
                approver_name = st.text_input("Authorizing Officer Name:", value="Branch Director Robert Vance")
                review_notes = st.text_area("Authorization / Reason Notes:", value="Reviewed relationship profitability, LTV, and risk tier. Concession justified.")

                btn_approve, btn_reject = st.columns(2)
                with btn_approve:
                    approve_submitted = st.form_submit_button("✅ Approve Concession", use_container_width=True)
                with btn_reject:
                    reject_submitted = st.form_submit_button("❌ Reject Concession", use_container_width=True)

                if approve_submitted:
                    result = retention_service.review_concession_approval(
                        case_id=target_p_id,
                        approver_name=approver_name,
                        approver_role=approver_role,
                        approved=True,
                        notes=review_notes
                    )
                    if result["success"]:
                        st.success(f"✅ Concession for Case {target_p_id} APPROVED! Status transitioned to 'Offer Proposed'.")
                        st.rerun()
                    else:
                        st.error(f"❌ Authorization Denied: {result.get('error')}")

                if reject_submitted:
                    result = retention_service.review_concession_approval(
                        case_id=target_p_id,
                        approver_name=approver_name,
                        approver_role=approver_role,
                        approved=False,
                        notes=review_notes or "Concession rejected due to margin policy thresholds."
                    )
                    if result["success"]:
                        st.warning(f"🚫 Concession for Case {target_p_id} REJECTED. Case returned to 'Contacted'.")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('error')}")

# =========================================================================
# TAB 3: REAL-TIME STREAMING & CAPITAL FLIGHT MONITOR
# =========================================================================
with tab_streaming:
    st.markdown("#### ⚡ **Real-Time Event Streaming & Capital Flight Monitor**")
    st.markdown("""
    BankSight continuously analyzes live transaction velocity streams. When a transaction indicates **Capital Flight**
    (e.g., balance withdrawal $\\ge 30\\%$ or $\\ge \\$25,000$), or multiple high-severity complaints occur, the engine
    immediately dispatches high-priority webhooks and automatically escalates or creates an emergency retention case.
    """)

    stream_col1, stream_col2 = st.columns([3, 2])

    with stream_col1:
        st.markdown("##### 🚨 **Live Dispatched Webhook Alerts**")
        webhooks = stream_processor.get_dispatched_webhooks(limit=20)
        if webhooks:
            for wh in reversed(webhooks):
                badge_color = BANK_RED if wh["severity"] == "Critical" else "#F7B731"
                st.markdown(
                    f"""
                    <div style="background-color: #FFFFFF; border-left: 5px solid {badge_color}; border-radius: 6px; padding: 12px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 700; color: #1E293B; font-size: 14px;">{wh['alert_title']}</span>
                            <span style="background-color: {badge_color}; color: #FFFFFF; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 10px;">{wh['severity']}</span>
                        </div>
                        <div style="font-size: 12px; color: #475569; margin-bottom: 4px;">{wh['summary']}</div>
                        <div style="font-size: 11px; color: #64748B;">
                            <strong>Customer ID:</strong> {wh['customer_id']} &nbsp;|&nbsp; <strong>Branch:</strong> {wh['branch_id']} &nbsp;|&nbsp; <strong>Trigger:</strong> {wh['trigger_type']} &nbsp;|&nbsp; <em>{wh['timestamp'][:19]}</em>
                        </div>
                        <div style="font-size: 11px; color: #0C2340; margin-top: 4px; background: #F1F5F9; padding: 4px 8px; border-radius: 4px;">
                            <strong>Recommended RM Action:</strong> {wh['recommended_action']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No webhook alerts dispatched yet in this session. Use the simulator on the right to trigger real-time events.")

    with stream_col2:
        st.markdown("##### 🧪 **Live Attrition Velocity Simulator**")
        st.markdown("Simulate high-velocity Core Banking ledger events to test real-time triggers and automated retention casework:")

        sim_type = st.radio("Select Event Simulation Type:", ["Large Balance Withdrawal (Capital Flight)", "Service Complaint Escalation"])

        if sim_type == "Large Balance Withdrawal (Capital Flight)":
            with st.form("sim_withdrawal_form"):
                sim_cust_id = st.text_input("Customer ID:", value="CUST-000001")
                sim_prior_bal = st.number_input("Prior Balance ($ USD):", min_value=1000.0, value=75000.0, step=5000.0)
                sim_with_amt = st.number_input("Withdrawal Amount ($ USD):", min_value=100.0, value=35000.0, step=5000.0)
                sim_channel = st.selectbox("Channel:", ["Wire Transfer", "Online Banking", "Branch Counter", "ATM"])

                calc_drop = (sim_with_amt / sim_prior_bal) * 100
                st.caption(f"Projected Balance Drop: **{calc_drop:.1f}%** (Trigger threshold: $\\ge 30\\%$ or $\\ge \\$25,000$)")

                trigger_btn = st.form_submit_button("🚀 Inject Live Streaming Transaction Event")

                if trigger_btn:
                    new_bal = max(0.0, sim_prior_bal - sim_with_amt)
                    event = LargeWithdrawalEvent(
                        transaction_id=f"TX-SIM-{datetime.now().strftime('%H%M%S')}",
                        customer_id=sim_cust_id,
                        account_id="ACC-SIM-001",
                        amount=sim_with_amt,
                        prior_balance=sim_prior_bal,
                        new_balance=new_bal,
                        channel=sim_channel,
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
                    alert = stream_processor.process_withdrawal_event(event)
                    if alert:
                        st.success(f"🚨 **CAPITAL FLIGHT TRIGGERED!** Alert dispatched: {alert.alert_title}")
                        st.caption("Emergency retention case auto-escalated in database. Check Queue.")
                    else:
                        st.info("ℹ️ Transaction processed normally. Velocity thresholds not breached.")
                    st.rerun()

        else:
            with st.form("sim_complaint_form"):
                sim_cust_id_c = st.text_input("Customer ID:", value="CUST-000002")
                sim_category = st.selectbox("Complaint Category:", ["Branch Service", "Fee Disputes", "Mobile App Failure", "Loan Processing Delay"])
                sim_severity = st.selectbox("Severity:", ["Critical", "High", "Medium", "Low"])
                sim_subject = st.text_input("Subject:", value="Client threatened to close account due to repeated fee assessment.")

                complaint_btn = st.form_submit_button("🚀 Inject Service Friction Stream Event")

                if complaint_btn:
                    event_c = ComplaintLoggedEvent(
                        complaint_id=f"CMP-SIM-{datetime.now().strftime('%H%M%S')}",
                        customer_id=sim_cust_id_c,
                        category=sim_category,
                        severity=sim_severity,
                        subject=sim_subject,
                        channel="Customer Support Hot-line",
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
                    alert_c = stream_processor.process_complaint_event(event_c)
                    if alert_c:
                        st.warning(f"⚠️ **COMPLAINT ESCALATION TRIGGERED!** Alert dispatched: {alert_c.alert_title}")
                    else:
                        st.info("ℹ️ Complaint logged with standard priority.")
                    st.rerun()
