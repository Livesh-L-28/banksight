"""
BankSight Branch Performance & Regional Benchmarking Studio
Branch deposit rankings, customer counts, attrition rates, regional comparisons, and underperforming unit alerts.
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
from backend.services.branch_service import BranchService

st.set_page_config(page_title="Branch Analytics | BankSight", page_icon="🏢", layout="wide")
apply_banking_theme()

render_page_header(
    title="Branch Network Performance & Regional Benchmarking",
    subtitle="Deposit volume rankings, customer attrition benchmarks, regional distribution, and frontline operational guidance",
    badge_text="Module 8 — Branch Analytics"
)

branch_service = BranchService()
rankings = branch_service.get_branch_rankings()
regional = branch_service.get_regional_summary()

if rankings:
    r_df = pd.DataFrame(rankings)
    reg_df = pd.DataFrame(regional)

    total_dep = r_df["total_deposits"].sum()
    top_branch = r_df.iloc[0]
    lowest_churn_branch = r_df.loc[r_df["churn_rate_pct"].idxmin()]
    underperforming_count = (r_df["performance_tier"] == "Underperforming").sum()

    # Top KPI Row
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        render_metric_card("Total Active Branches", f"{len(r_df)}", f"Across {len(reg_df)} Regions")
    with b2:
        render_metric_card("Top Branch (Deposits)", top_branch["branch_name"], format_currency(top_branch["total_deposits"]))
    with b3:
        render_metric_card("Lowest Churn Branch", lowest_churn_branch["branch_name"], f"{lowest_churn_branch['churn_rate_pct']:.1f}% Attrition", delta_color=BANK_GREEN)
    with b4:
        render_metric_card("Underperforming Units", f"{underperforming_count}", "Requires Intervention Alert", delta_color=BANK_RED if underperforming_count > 0 else BANK_GREEN)

    st.markdown("<br>", unsafe_allow_html=True)

    # Branch Rankings Table
    st.markdown("##### 🏆 **Branch Performance Rankings**")
    st.dataframe(
        r_df[[
            "rank", "branch_name", "city", "state", "region",
            "total_customers", "total_deposits", "avg_balance_per_account",
            "churn_rate_pct", "performance_tier"
        ]].rename(columns={
            "rank": "Rank",
            "branch_name": "Branch Name",
            "city": "City",
            "state": "State",
            "region": "Region",
            "total_customers": "Customers",
            "total_deposits": "Total Deposits ($)",
            "avg_balance_per_account": "Avg Balance / Acc ($)",
            "churn_rate_pct": "Churn Rate (%)",
            "performance_tier": "Status Tier"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations Row: Deposits & Regional Share
    v1, v2 = st.columns([3, 2])
    with v1:
        st.markdown("##### 📊 **Deposit Distribution by Branch**")
        fig_b = px.bar(
            r_df,
            x="total_deposits",
            y="branch_name",
            orientation="h",
            color="churn_rate_pct",
            color_continuous_scale=["#DEF7EC", "#FDE8E8", BANK_RED],
            labels={"total_deposits": "Deposits ($)", "branch_name": "Branch", "churn_rate_pct": "Churn %"}
        )
        fig_b.update_layout(yaxis=dict(autorange="reversed"), **get_banking_chart_layout("Deposits & Churn Intensity", height=350))
        st.plotly_chart(fig_b, use_container_width=True)

    with v2:
        st.markdown("##### 🗺️ **Regional Deposit Share**")
        fig_reg = px.pie(
            reg_df,
            names="region",
            values="regional_deposits",
            hole=0.5,
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731", "#20BF6B"]
        )
        fig_reg.update_layout(**get_banking_chart_layout("Regional Liquidity Distribution", height=350))
        st.plotly_chart(fig_reg, use_container_width=True)

    # Underperforming Alert & Guidance
    if underperforming_count > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(
            f"""
            ⚠️ **Management Intervention Advisory:**
            {underperforming_count} branch unit(s) currently exhibit elevated churn (>20%) or lower customer bases. Regional leadership should schedule operational reviews to audit local customer complaints, evaluate RM portfolio sizes, and deploy localized deposit retention campaigns.
            """
        )
