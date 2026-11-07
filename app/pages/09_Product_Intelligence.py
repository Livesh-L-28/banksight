"""
BankSight Product Intelligence & Cross-Selling Studio
Product catalog penetration, portfolio depth, and transparent rule-based cross-sell recommendation engine.
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
    format_currency, get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN
)
from backend.services.product_service import ProductService

st.set_page_config(page_title="Product Intelligence | BankSight", page_icon="💎", layout="wide")
apply_banking_theme()

render_page_header(
    title="Product Portfolio Intelligence & Cross-Selling",
    subtitle="Product penetration depth, multi-holding customer dynamics, and transparent rule-based cross-sell opportunities",
    badge_text="Module 9 — Product Analytics"
)

product_service = ProductService()
portfolio = product_service.get_portfolio_penetration()
cross_sells = product_service.get_cross_sell_leads()

if portfolio:
    p_df = pd.DataFrame(portfolio)
    total_enrolled = p_df["enrolled_customers"].sum()
    top_prod = p_df.iloc[0]

    # Top KPI Row
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        render_metric_card("Catalog Products", f"{len(p_df)}", "Active Product Offerings")
    with p2:
        render_metric_card("Top Product by Penetration", top_prod["product_name"], f"{top_prod['penetration_rate_pct']:.1f}% Penetration")
    with p3:
        render_metric_card("Cross-Sell Qualified Leads", f"{len(cross_sells)}", "High-Propensity Candidates")
    with p4:
        render_metric_card("Products / Customer", f"{total_enrolled / 1000.0:.2f}", "Portfolio Depth Metric")

    st.markdown("<br>", unsafe_allow_html=True)

    # Product Penetration Table & Chart
    v1, v2 = st.columns([3, 2])

    with v1:
        st.markdown("##### 📊 **Product Penetration Across Catalog**")
        fig_p = px.bar(
            p_df,
            x="penetration_rate_pct",
            y="product_name",
            orientation="h",
            color="category",
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731"],
            labels={"penetration_rate_pct": "Penetration Rate (%)", "product_name": "Product"}
        )
        fig_p.update_layout(yaxis=dict(autorange="reversed"), **get_banking_chart_layout("Customer Adoption by Product (%)", height=340))
        st.plotly_chart(fig_p, use_container_width=True)

    with v2:
        st.markdown("##### 🏛️ **Product Portfolio Holdings Summary**")
        st.dataframe(
            p_df[[
                "product_name", "category", "interest_rate_pct", "annual_fee",
                "enrolled_customers", "penetration_rate_pct"
            ]].rename(columns={
                "product_name": "Product Name",
                "category": "Category",
                "interest_rate_pct": "Rate (%)",
                "annual_fee": "Fee ($)",
                "enrolled_customers": "Enrolled",
                "penetration_rate_pct": "Penetration (%)"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Cross-Selling Opportunity Engine
    st.markdown("##### 🎯 **Rule-Based Cross-Sell & Up-Sell Opportunities**")
    st.caption("Candidates identified via transparent financial rules (surplus liquidity, prime credit score, single-product holders). Advisory only.")

    if cross_sells:
        cs_df = pd.DataFrame(cross_sells)
        st.dataframe(
            cs_df[[
                "customer_id", "customer_name", "annual_income", "current_balance",
                "recommended_product", "opportunity_type", "rationale"
            ]].rename(columns={
                "customer_id": "Cust ID",
                "customer_name": "Customer Name",
                "annual_income": "Income ($)",
                "current_balance": "Balance ($)",
                "recommended_product": "Target Product Recommendation",
                "opportunity_type": "Opportunity Type",
                "rationale": "Transparent Qualification Rationale"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "📥 Export Cross-Sell Leads (.csv)",
            data=cs_df.to_csv(index=False).encode("utf-8"),
            file_name="banksight_cross_sell_leads.csv",
            mime="text/csv"
        )
else:
    st.info("No product catalog data available.")

