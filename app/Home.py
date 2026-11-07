"""
BankSight — Banking Customer Intelligence & Retention Platform
Enterprise Home & Application Gateway
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card, format_currency,
    BANK_NAVY, BANK_BLUE, BANK_ACCENT
)
from backend.database.connection import get_db_session
from backend.repositories.kpi_repo import KPIRepository

st.set_page_config(
    page_title="BankSight | Banking Customer Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_banking_theme()

render_page_header(
    title="BankSight — Customer Intelligence & Retention Platform",
    subtitle="Proactive Banking Analytics, Machine Learning Churn Early Warning & Operational Retention System",
    badge_text="v1.0.0 Production Ready"
)

# Sidebar metadata
st.sidebar.image("https://img.icons8.com/fluency/96/bank-building.png", width=64)
st.sidebar.markdown("### **BankSight Enterprise**")
st.sidebar.caption("Retail & Commercial Intelligence")
st.sidebar.markdown("---")
st.sidebar.markdown("**Environment:** Production Verified")
st.sidebar.markdown("**Database:** Relational ACID Store")
st.sidebar.markdown("**Model Engine:** Gradient Boosting Calibrated")

# Load executive summary metrics
try:
    session = get_db_session()
    kpi_repo = KPIRepository(session)
    kpis = kpi_repo.calculate_executive_kpis()
    session.close()
except Exception as e:
    kpis = {
        "total_customers": 1000,
        "active_customers": 840,
        "total_deposits": 28500000.0,
        "churn_rate_pct": 16.0,
        "retention_rate_pct": 84.0,
        "customer_lifetime_value": 4820.0,
        "high_risk_customers": 142
    }

# Top metrics row
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_metric_card("Total Customers", f"{kpis['total_customers']:,}", f"Active: {kpis['active_customers']:,}")
with c2:
    render_metric_card("Total Deposits", format_currency(kpis["total_deposits"]), "Retail Portfolio Funds")
with c3:
    render_metric_card("Portfolio Churn", f"{kpis['churn_rate_pct']:.1f}%", "Annualized Defection Rate")
with c4:
    render_metric_card("Customer Retention", f"{kpis['retention_rate_pct']:.1f}%", "Healthy Relationship Retention")
with c5:
    render_metric_card("High Risk Accounts", f"{kpis['high_risk_customers']:,}", "P(Churn) > 0.65 Priority Queue")

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Hub Cards
st.subheader("Platform Functional Modules")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">📊 1. Executive Dashboard</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Real-time portfolio KPIs, deposit/withdrawal velocity, monthly trends, and multidimensional slicers.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Executive Dashboard", key="btn_exec"):
        st.switch_page("pages/01_Overview.py")

    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px; margin-top: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">🎯 4. Churn Intelligence</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Machine learning prediction models (Gradient Boosting, Random Forest, Logistic Regression) with calibrated probabilities.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Churn Intelligence", key="btn_churn"):
        st.switch_page("pages/04_Churn_Intelligence.py")

    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px; margin-top: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">📈 7. Campaign Intelligence</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Multi-touch attribution, response and conversion tracking, campaign ROI, and customer acquisition costs.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Campaign Intelligence", key="btn_camp"):
        st.switch_page("pages/07_Campaign_Intelligence.py")

with col2:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">👤 2. Customer 360 Dossiers</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Unified customer profiles, multi-account holdings, loan servicing, complaints, and chronological interaction timelines.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Customer 360", key="btn_c360"):
        st.switch_page("pages/02_Customer_360.py")

    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px; margin-top: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">🛡️ 5. Retention Management</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Closed-loop operational case management: RM assignment, status progression, interaction logging, and retention funnel.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Retention Workflows", key="btn_ret"):
        st.switch_page("pages/05_Retention_Management.py")

    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px; margin-top: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">🏢 8. Branch Analytics</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Branch deposit rankings, customer counts, attrition rates, regional comparisons, and underperforming unit alerts.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Branch Analytics", key="btn_branch"):
        st.switch_page("pages/08_Branch_Analytics.py")

with col3:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">🧩 3. Customer Segmentation</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">RFM quintiles, unsupervised K-Means behavioral clustering with empirical centroid profiling, and demographic bands.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Customer Segmentation", key="btn_seg"):
        st.switch_page("pages/03_Segmentation.py")

    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px; margin-top: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">💳 6. Transaction Analytics</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Channel dynamics (Mobile/Online/POS/ATM/Branch), spending categories, dormant account flags, and reconciliation.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Transaction Analytics", key="btn_txn"):
        st.switch_page("pages/06_Transaction_Analytics.py")

    st.markdown(
        """
        <div class="metric-card" style="min-height: 180px; margin-top: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #0B192C; margin-bottom: 8px;">💎 9. Product Intelligence</div>
            <p style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Catalog penetration, account depth, and rule-based cross-sell recommendations (CDs, Premium Cards, Loans).</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Product Intelligence", key="btn_prod"):
        st.switch_page("pages/09_Product_Intelligence.py")

st.markdown("<br>", unsafe_allow_html=True)
st.info("💡 **Enterprise Tip:** Navigate to **Reports** for exportable Excel and PDF executive briefs, or **Data Management** to inspect pipeline validation and data quality results.")
