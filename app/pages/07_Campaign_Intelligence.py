"""
BankSight Campaign Intelligence & Attribution Studio
Campaign tracking, multi-touch attribution, conversion rates, marketing ROI, and CAC benchmarks.
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
from backend.services.campaign_service import CampaignService

st.set_page_config(page_title="Campaign Intelligence | BankSight", page_icon="📈", layout="wide")
apply_banking_theme()

render_page_header(
    title="Marketing Campaign Intelligence & Attribution",
    subtitle="Campaign response metrics, multi-touch revenue attribution, return on investment (ROI), and acquisition efficiency",
    badge_text="Module 7 — Marketing Analytics"
)

campaign_service = CampaignService()
campaigns = campaign_service.get_campaign_performance()

if campaigns:
    camp_df = pd.DataFrame(campaigns)

    total_budget = camp_df["budget"].sum()
    total_rev = camp_df["attributed_revenue"].sum()
    total_reach = camp_df["reach"].sum()
    total_conversions = camp_df["conversions"].sum()
    avg_roi = round(((total_rev - total_budget) / max(total_budget, 1.0)) * 100, 1)
    avg_cpa = round(total_budget / max(total_conversions, 1), 2)

    # Top KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Total Campaigns", f"{len(camp_df)}", "Active & Completed")
    with c2:
        render_metric_card("Total Reach", f"{total_reach:,}", f"{total_conversions:,} Conversions")
    with c3:
        render_metric_card("Total Marketing Spend", format_currency(total_budget), "Allocated Budget")
    with c4:
        render_metric_card("Attributed Revenue", format_currency(total_rev), f"Net ROI: {avg_roi:.1f}%")
    with c5:
        render_metric_card("Cost Per Acquisition", format_currency(avg_cpa), "Portfolio Blended CPA")

    st.markdown("<br>", unsafe_allow_html=True)

    # Performance Table
    st.markdown("##### 📋 **Campaign Performance & ROI Scorecard**")
    st.dataframe(
        camp_df[[
            "campaign_name", "objective", "target_segment", "channel",
            "budget", "reach", "responses", "conversions", "response_rate_pct",
            "conversion_rate_pct", "attributed_revenue", "roi_pct", "cpa"
        ]].rename(columns={
            "campaign_name": "Campaign Name",
            "objective": "Objective",
            "target_segment": "Target Segment",
            "channel": "Channel",
            "budget": "Budget ($)",
            "reach": "Reach",
            "responses": "Responses",
            "conversions": "Conversions",
            "response_rate_pct": "Response %",
            "conversion_rate_pct": "Conv %",
            "attributed_revenue": "Attributed Rev ($)",
            "roi_pct": "ROI (%)",
            "cpa": "CPA ($)"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations: ROI and Reach vs Conversion
    v1, v2 = st.columns([1, 1])
    with v1:
        st.markdown("##### 💰 **Marketing ROI by Campaign (%)**")
        fig_roi = px.bar(
            camp_df,
            x="campaign_code",
            y="roi_pct",
            color="roi_pct",
            color_continuous_scale=["#CBD5E1", BANK_NAVY],
            labels={"campaign_code": "Campaign", "roi_pct": "Net ROI (%)"}
        )
        fig_roi.update_layout(**get_banking_chart_layout("Campaign ROI Comparison (%)", height=320))
        st.plotly_chart(fig_roi, use_container_width=True)

    with v2:
        st.markdown("##### 🎯 **Reach vs. Conversion Efficiency**")
        fig_reach = px.scatter(
            camp_df,
            x="reach",
            y="conversions",
            size="budget",
            color="objective",
            hover_name="campaign_name",
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731"],
            labels={"reach": "Audience Reach", "conversions": "Conversions"}
        )
        fig_reach.update_layout(**get_banking_chart_layout("Campaign Volume vs Conversion", height=320))
        st.plotly_chart(fig_reach, use_container_width=True)

    # Attribution Documentation Alert
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        """
        ℹ️ **Attribution Methodology Standard:**
        BankSight employs a 30-day time-decay attribution model connecting customer campaign exposure to subsequent product enrollments and incremental deposit growth. Correlation is monitored against control cohorts to prevent baseline bias.
        """
    )
else:
    st.info("No campaign data available.")
