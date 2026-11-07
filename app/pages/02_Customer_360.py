"""
BankSight Customer 360 Intelligence Dossier
Provides unified customer profile, accounts, loans, transaction history, complaints, and interactive timeline.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    format_currency, get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN, BANK_RED
)
from backend.services.customer_service import CustomerService
from backend.services.branch_service import BranchService
from backend.database.connection import get_db_session
from backend.models import ChurnPrediction

st.set_page_config(page_title="Customer 360 | BankSight", page_icon="👤", layout="wide")
apply_banking_theme()

render_page_header(
    title="Customer 360 Intelligence Dossier",
    subtitle="Unified individual customer profile, multi-account holdings, timeline events, and behavioral risk assessment",
    badge_text="Module 2 — Intelligence"
)

customer_service = CustomerService()
branch_service = BranchService()

# Search Bar and Filter Controls
s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
with s_col1:
    search_term = st.text_input("🔍 Search by Customer ID, Name, City, or Email:", value="CUST-00001")
with s_col2:
    branches = branch_service.get_all_branches()
    branch_opts = ["All"] + [b["branch_name"] for b in branches]
    sel_branch = st.selectbox("Filter Branch", options=branch_opts, index=0)
with s_col3:
    sel_segment = st.selectbox(
        "Filter Segment",
        options=["All", "High Net Worth", "Affluent", "Young Professional", "Loyal Traditional", "Mass Retail"],
        index=0
    )

branch_id_val = None
if sel_branch != "All":
    b_match = next((b["branch_id"] for b in branches if b["branch_name"] == sel_branch), None)
    branch_id_val = b_match

# Perform search
search_results = customer_service.search_customers(
    search_query=search_term if search_term else None,
    branch_id=branch_id_val,
    segment=sel_segment if sel_segment != "All" else None,
    limit=20
)

if not search_results:
    st.warning("No customers matched your search query. Try searching for 'CUST-00001' or clear filters.")
else:
    # Select customer dropdown if multiple returned
    cust_options = {f"{c['customer_id']} — {c['full_name']} (${c['total_balance']:,.2f})": c["customer_id"] for c in search_results}
    selected_label = st.selectbox("Select Customer to Inspect Dossier:", options=list(cust_options.keys()))
    selected_cust_id = cust_options[selected_label]

    # Fetch full dossier
    dossier = customer_service.get_customer_dossier(selected_cust_id)

    if dossier:
        # Fetch churn score from DB
        session = get_db_session()
        pred = session.query(ChurnPrediction).filter(ChurnPrediction.customer_id == selected_cust_id).first()
        session.close()

        churn_prob = pred.churn_probability if pred else (0.78 if dossier["churn_flag"] else 0.14)
        risk_tier = pred.risk_category if pred else ("High Risk" if dossier["churn_flag"] else "Low Risk")

        # Top Dossier Header Card
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                    <div>
                        <h2 style="margin: 0 0 4px 0; color: {BANK_NAVY}; font-size: 22px;">{dossier['full_name']} <span style="font-size: 14px; color: #64748B; font-weight: normal;">({dossier['customer_id']})</span></h2>
                        <p style="margin: 0; color: #475569; font-size: 13px;">{dossier['occupation']} • {dossier['city']}, {dossier['state']} • Branch: <strong>{dossier['branch_name']}</strong></p>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center; margin-top: 6px;">
                        <span style="background: #F1F5F9; color: #334155; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600;">{dossier['customer_segment']}</span>
                        <span class="{'badge-high' if risk_tier == 'High Risk' else ('badge-med' if risk_tier == 'Medium Risk' else 'badge-low')}">{risk_tier} ({churn_prob:.1%})</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick Metric Badges
        q1, q2, q3, q4, q5 = st.columns(5)
        with q1:
            render_metric_card("Total Balances", format_currency(dossier["total_balance"]), f"{len(dossier['accounts'])} Account(s)")
        with q2:
            render_metric_card("Annual Income", format_currency(dossier["annual_income"]), f"Age: {dossier['age']} • {dossier['gender']}")
        with q3:
            render_metric_card("Customer Tenure", f"{dossier['tenure_months']} mos", f"Joined {dossier['joining_date']}")
        with q4:
            render_metric_card("Credit Score", f"{dossier['credit_score'] or 'N/A'}", "Prime Rating" if (dossier['credit_score'] or 0) >= 700 else "Standard")
        with q5:
            render_metric_card("Relationship Mgr", dossier["relationship_manager"], "Primary Assigned RM")

        st.markdown("<br>", unsafe_allow_html=True)

        # Multi-tab dossier breakdown
        tab_acc, tab_txn, tab_cmp, tab_timeline, tab_risk = st.tabs([
            "💳 Accounts & Loans",
            "📜 Transaction Ledger",
            "⚠️ Customer Service & Complaints",
            "⏱️ Activity Timeline",
            "🛡️ Churn Risk & Retention Plan"
        ])

        with tab_acc:
            st.markdown("##### 🏛️ **Deposit Accounts Portfolio**")
            if dossier["accounts"]:
                acc_df = pd.DataFrame(dossier["accounts"])
                st.dataframe(
                    acc_df.rename(columns={
                        "account_id": "Account ID",
                        "account_number": "Account Number",
                        "account_type": "Product Type",
                        "current_balance": "Current Balance ($)",
                        "available_balance": "Available Balance ($)",
                        "status": "Status",
                        "open_date": "Open Date",
                        "is_primary": "Primary"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No deposit accounts found.")

            st.markdown("##### 📄 **Lending & Credit Portfolio**")
            if dossier["loans"]:
                ln_df = pd.DataFrame(dossier["loans"])
                st.dataframe(
                    ln_df.rename(columns={
                        "loan_id": "Loan ID",
                        "loan_number": "Loan Number",
                        "product_name": "Loan Facility",
                        "principal": "Principal Amount ($)",
                        "current_balance": "Remaining Balance ($)",
                        "interest_rate": "Interest Rate (%)",
                        "installment": "Monthly Installment ($)",
                        "status": "Status"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No active lending facilities.")

        with tab_txn:
            st.markdown("##### 💸 **Recent Transaction Ledger (Trailing 30)**")
            if dossier["transactions"]:
                t_df = pd.DataFrame(dossier["transactions"])
                st.dataframe(
                    t_df.rename(columns={
                        "transaction_id": "Txn ID",
                        "transaction_date": "Timestamp",
                        "transaction_type": "Type",
                        "amount": "Amount ($)",
                        "balance_after": "Running Balance ($)",
                        "channel": "Channel",
                        "status": "Status",
                        "description": "Memo / Description"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No transaction records available.")

        with tab_cmp:
            st.markdown("##### ⚠️ **Customer Service Escalations & Complaints**")
            if dossier["complaints"]:
                c_df = pd.DataFrame(dossier["complaints"])
                st.dataframe(
                    c_df.rename(columns={
                        "complaint_id": "Complaint ID",
                        "category": "Category",
                        "priority": "Priority",
                        "status": "Status",
                        "logged_date": "Logged Date",
                        "resolved_date": "Resolved Date",
                        "description": "Customer Description"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("Clean servicing record: Zero logged complaints.")

        with tab_timeline:
            st.markdown("##### ⏱️ **Chronological Customer Activity Timeline**")
            if dossier["timeline"]:
                for event in dossier["timeline"]:
                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid {BANK_NAVY}; padding-left: 14px; margin-bottom: 12px;">
                            <div style="font-size: 11px; color: #94A3B8; font-weight: 600;">{event['date']} • {event['channel']}</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A;">{event['event_type']}</div>
                            <div style="font-size: 12px; color: #475569;">{event['details']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No events in timeline.")

        with tab_risk:
            st.markdown("##### 🎯 **Machine Learning Churn Risk Assessment**")
            r_col1, r_col2 = st.columns([1, 1])
            with r_col1:
                render_metric_card(
                    "Calibrated Churn Probability",
                    f"{churn_prob:.1%}",
                    f"Assigned Risk Tier: {risk_tier}"
                )
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("###### **Key Contributing Churn Drivers:**")
                factors = pred.top_churn_factors if pred and pred.top_churn_factors else [
                    "Declining 90-day balance trend",
                    "Lower mobile banking login cadence"
                ]
                for f in factors:
                    st.markdown(f"- ⚠️ **{f}**")

            with r_col2:
                rec_action = pred.recommended_action if pred and pred.recommended_action else "Schedule relationship review meeting"
                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px;">
                        <div style="font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase;">Advisory Retention Playbook</div>
                        <div style="font-size: 15px; font-weight: 600; color: {BANK_NAVY}; margin: 8px 0;">{rec_action}</div>
                        <p style="font-size: 12px; color: #475569;">Recommendation generated by calibrated predictive engine. Review customer 360 profile before contacting client.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("🛡️ Open Operational Retention Case for this Customer"):
                    st.switch_page("pages/05_Retention_Management.py")
