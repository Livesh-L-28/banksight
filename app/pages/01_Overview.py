"""
BankSight Executive Intelligence Dashboard
Real-time portfolio KPIs, interactive multidimensional slicing, trend analytics, and drill-down exports.
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    format_currency, get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN, BANK_RED
)
from backend.database.connection import get_db_session
from backend.repositories.kpi_repo import KPIRepository
from backend.services.branch_service import BranchService
from backend.services.customer_service import CustomerService

st.set_page_config(page_title="Executive Dashboard | BankSight", page_icon="📊", layout="wide")
apply_banking_theme()

render_page_header(
    title="Executive Banking Intelligence Dashboard",
    subtitle="Strategic portfolio balance, customer health dynamics, deposit flows, and retention KPIs",
    badge_text="Module 1 — Executive"
)

# Sidebar Filters
st.sidebar.markdown("### 🎛️ **Dashboard Slicers**")

branch_service = BranchService()
branches = branch_service.get_all_branches()
branch_options = {b["branch_name"]: b["branch_id"] for b in branches}

selected_branches = st.sidebar.multiselect(
    "Select Branches",
    options=list(branch_options.keys()),
    default=[]
)
selected_branch_ids = [branch_options[b] for b in selected_branches] if selected_branches else None

segment_options = ["High Net Worth", "Affluent", "Young Professional", "Loyal Traditional", "Mass Retail"]
selected_segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=segment_options,
    default=[]
)
selected_segment_filter = selected_segments if selected_segments else None

# Date Range Filter
date_col1, date_col2 = st.sidebar.columns(2)
with date_col1:
    start_date = st.date_input("Start Date", value=date(2020, 1, 1))
with date_col2:
    end_date = st.date_input("End Date", value=date(2026, 11, 1))

# Load KPIs
session = get_db_session()
kpi_repo = KPIRepository(session)
kpis = kpi_repo.calculate_executive_kpis(
    start_date=start_date,
    end_date=end_date,
    branch_ids=selected_branch_ids,
    customer_segments=selected_segment_filter
)
monthly_trends = kpi_repo.get_monthly_transaction_trend(
    branch_ids=selected_branch_ids,
    customer_segments=selected_segment_filter
)
session.close()

# KPI Row 1
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    render_metric_card("Total Customers", f"{kpis['total_customers']:,}", f"Active Base: {kpis['active_customers']:,}")
with k2:
    render_metric_card("Total Deposits", format_currency(kpis["total_deposits"]), f"Avg / Cust: {format_currency(kpis['average_customer_balance'])}")
with k3:
    render_metric_card("Annualized Churn", f"{kpis['churn_rate_pct']:.1f}%", f"Retained: {kpis['retention_rate_pct']:.1f}%")
with k4:
    render_metric_card("ARPU (Annual)", format_currency(kpis["arpu"]), "Spread + Net Fees")
with k5:
    render_metric_card("Customer Lifetime Value", format_currency(kpis["customer_lifetime_value"]), "Projected Remaining Value")

# KPI Row 2
k6, k7, k8, k9, k10 = st.columns(5)
with k6:
    render_metric_card("Total Accounts", f"{kpis['total_accounts']:,}", "Checking, Savings & CDs")
with k7:
    render_metric_card("Total Withdrawals", format_currency(kpis["total_withdrawals"]), "Spend & Transfers Out")
with k8:
    render_metric_card("Transaction Volume", format_currency(kpis["total_transaction_value"]), "Gross Payment Turnover")
with k9:
    render_metric_card("High Risk Accounts", f"{kpis['high_risk_customers']:,}", "P(Churn) > 0.65 Queue")
with k10:
    render_metric_card("Campaign Conversion", f"{kpis['campaign_conversion_rate']:.1f}%", "Attributed Outreach")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row 1
v_col1, v_col2 = st.columns([3, 2])

with v_col1:
    st.markdown("##### 📈 **Monthly Cashflow & Deposit vs Withdrawal Trend**")
    if monthly_trends:
        trend_df = pd.DataFrame(monthly_trends)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=trend_df["month"],
            y=trend_df["deposits"],
            name="Inbound Deposits",
            marker_color=BANK_NAVY
        ))
        fig_trend.add_trace(go.Bar(
            x=trend_df["month"],
            y=trend_df["withdrawals"],
            name="Outbound Withdrawals",
            marker_color=BANK_RED
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_df["month"],
            y=trend_df["net_flow"],
            name="Net Liquidity Flow",
            line=dict(color=BANK_GREEN, width=3),
            mode="lines+markers"
        ))
        fig_trend.update_layout(
            barmode="group",
            **get_banking_chart_layout("Monthly Deposit & Withdrawal Flows ($)", height=350)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No transaction data available for selected filter window.")

with v_col2:
    st.markdown("##### 👥 **Customer Segment Composition**")
    # Load segment distribution
    cust_service = CustomerService()
    cust_data = cust_service.search_customers(
        branch_id=selected_branch_ids[0] if selected_branch_ids and len(selected_branch_ids) == 1 else None,
        segment=selected_segment_filter[0] if selected_segment_filter and len(selected_segment_filter) == 1 else None,
        limit=1000
    )
    if cust_data:
        cdf = pd.DataFrame(cust_data)
        seg_counts = cdf["customer_segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]

        fig_seg = px.pie(
            seg_counts,
            names="Segment",
            values="Count",
            hole=0.55,
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731", "#20BF6B"]
        )
        fig_seg.update_layout(**get_banking_chart_layout("Portfolio Segment Distribution", height=350))
        st.plotly_chart(fig_seg, use_container_width=True)
    else:
        st.info("No customer records match filter criteria.")

# Visualizations Row 2: Branch Comparison & Drill-down
st.markdown("<br>", unsafe_allow_html=True)
v_col3, v_col4 = st.columns([2, 3])

with v_col3:
    st.markdown("##### 🏢 **Branch Deposit Benchmarking**")
    rankings = branch_service.get_branch_rankings()
    if rankings:
        br_df = pd.DataFrame(rankings).head(8)
        fig_br = px.bar(
            br_df,
            x="total_deposits",
            y="branch_name",
            orientation="h",
            color="total_deposits",
            color_continuous_scale=["#CBD5E1", BANK_NAVY],
            labels={"total_deposits": "Total Deposits ($)", "branch_name": "Branch"}
        )
        fig_br.update_layout(
            yaxis=dict(autorange="reversed"),
            **get_banking_chart_layout("Top Branches by Total Deposit Volume", height=340)
        )
        st.plotly_chart(fig_br, use_container_width=True)

with v_col4:
    st.markdown("##### 🔍 **Underlying Customer Cohort Records (Drill-Down)**")
    if cust_data:
        disp_df = pd.DataFrame(cust_data)[[
            "customer_id", "full_name", "city", "state",
            "customer_segment", "customer_status", "total_balance", "branch_name"
        ]].head(15)

        st.dataframe(
            disp_df.rename(columns={
                "customer_id": "Customer ID",
                "full_name": "Full Name",
                "city": "City",
                "state": "State",
                "customer_segment": "Segment",
                "customer_status": "Status",
                "total_balance": "Total Balance ($)",
                "branch_name": "Branch"
            }),
            use_container_width=True,
            hide_index=True
        )

        csv_data = pd.DataFrame(cust_data).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Cohort Data (.csv)",
            data=csv_data,
            file_name=f"banksight_executive_cohort_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No records to display.")

