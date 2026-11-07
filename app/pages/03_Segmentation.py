"""
BankSight Customer Segmentation Studio
Multi-criteria segmentation: RFM quintiles, unsupervised K-Means clustering, and demographic bands.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    format_currency, get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN
)
from backend.services.segmentation_service import SegmentationService
from analytics.segmentation.rfm import RFMSegmenter

st.set_page_config(page_title="Customer Segmentation | BankSight", page_icon="🧩", layout="wide")
apply_banking_theme()

render_page_header(
    title="Customer Segmentation & Behavioral Clustering",
    subtitle="RFM analysis, unsupervised K-Means clustering with empirical profiling, and segment playbooks",
    badge_text="Module 3 — Segmentation"
)

seg_service = SegmentationService()

# Controls
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
with ctrl_col1:
    seg_method = st.radio(
        "Select Segmentation Framework:",
        options=["RFM Segmentation", "K-Means Clustering", "Financial Balance Tiers", "Demographic Age Bands"],
        horizontal=True
    )
with ctrl_col2:
    k_clusters = st.slider("K-Means Clusters (k)", min_value=3, max_value=7, value=5)
with ctrl_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    recluster_btn = st.button("🔄 Execute Clustering")

# Run segmentation
with st.spinner("Computing customer segment distributions and behavioral profiles..."):
    results = seg_service.run_all_segmentations(n_clusters=k_clusters, persist=recluster_btn)

seg_df = results["segmented_dataframe"]

# Metric Cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Analyzed Customers", f"{len(seg_df):,}", "Full Retail Portfolio")
with m2:
    rfm_top = max(results["rfm_distribution"], key=lambda x: x["customer_count"])
    render_metric_card("Dominant RFM Cohort", rfm_top["segment_label"], f"{rfm_top['customer_count']:,} Customers")
with m3:
    sil_score = results["kmeans_evaluation"]["silhouette_score"]
    render_metric_card("K-Means Silhouette", f"{sil_score:.3f}", "Cluster Separation Quality")
with m4:
    render_metric_card("Configured Clusters", f"{k_clusters}", "Empirically Profiled")

st.markdown("<br>", unsafe_allow_html=True)

# Main Section based on chosen method
if seg_method == "RFM Segmentation":
    st.markdown("##### 📊 **RFM (Recency, Frequency, Monetary) Customer Distribution**")
    r_col1, r_col2 = st.columns([3, 2])

    with r_col1:
        rfm_dist_df = pd.DataFrame(results["rfm_distribution"])
        fig_rfm = px.bar(
            rfm_dist_df,
            x="segment_label",
            y="customer_count",
            color="segment_label",
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731", "#20BF6B", "#EB3B5A", "#4B6584", "#778CA3"],
            labels={"segment_label": "RFM Segment", "customer_count": "Customers"}
        )
        fig_rfm.update_layout(showlegend=False, **get_banking_chart_layout("RFM Segment Counts", height=340))
        st.plotly_chart(fig_rfm, use_container_width=True)

    with r_col2:
        st.markdown("##### 🎯 **Segment Action Playbook**")
        selected_rfm_seg = st.selectbox("Select Segment Playbook to Review:", options=rfm_dist_df["segment_label"].tolist())
        playbook = RFMSegmenter().get_segment_recommendations(selected_rfm_seg)

        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px;">
                <div style="font-size: 13px; font-weight: 700; color: {BANK_NAVY}; text-transform: uppercase;">Strategic Objective</div>
                <div style="font-size: 15px; font-weight: 600; color: #1E293B; margin: 4px 0 12px 0;">{playbook['objective']}</div>
                <div style="font-size: 13px; font-weight: 700; color: {BANK_NAVY}; text-transform: uppercase;">Recommended Interventions</div>
                <ul style="font-size: 13px; color: #475569; margin: 6px 0 12px 0; padding-left: 20px;">
                    {''.join(f'<li>{act}</li>' for act in playbook['recommended_actions'])}
                </ul>
                <div style="font-size: 12px; color: #64748B;">Target Campaign Affinity: <strong>{playbook['campaign_affinity']}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )

elif seg_method == "K-Means Clustering":
    st.markdown("##### 🔬 **K-Means Behavioral Centroid Profiles**")
    profiles_df = pd.DataFrame(results["cluster_profiles"])

    st.dataframe(
        profiles_df.rename(columns={
            "cluster_id": "Cluster #",
            "segment_label": "Empirical Business Label",
            "avg_balance": "Avg Balance ($)",
            "avg_income": "Avg Income ($)",
            "avg_txns_12m": "Avg Txns (12m)",
            "avg_tenure_months": "Avg Tenure (Mos)",
            "digital_adoption_pct": "Digital Adoption (%)",
            "avg_recency_days": "Avg Recency (Days)"
        }),
        use_container_width=True,
        hide_index=True
    )

    k_col1, k_col2 = st.columns([1, 1])
    with k_col1:
        fig_km = px.pie(
            profiles_df,
            names="segment_label",
            values="avg_balance",
            hole=0.5,
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731", "#20BF6B"]
        )
        fig_km.update_layout(**get_banking_chart_layout("Deposit Balance Share by Cluster", height=320))
        st.plotly_chart(fig_km, use_container_width=True)

    with k_col2:
        fig_scatter = px.scatter(
            seg_df,
            x="total_balance",
            y="annual_income",
            color="kmeans_segment",
            hover_data=["customer_id", "first_name", "last_name", "digital_txn_ratio"],
            labels={"total_balance": "Total Balance ($)", "annual_income": "Annual Income ($)"},
            color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731", "#20BF6B"]
        )
        fig_scatter.update_layout(**get_banking_chart_layout("Balance vs. Income Distribution", height=320))
        st.plotly_chart(fig_scatter, use_container_width=True)

else:
    # Demographic / Financial
    dist_key = "demographic_distribution" if "Demographic" in seg_method else "financial_distribution"
    dist_df = pd.DataFrame(results[dist_key])
    fig_d = px.bar(
        dist_df,
        x="segment_label",
        y="customer_count",
        color="segment_label",
        color_discrete_sequence=[BANK_NAVY, BANK_BLUE, BANK_ACCENT, "#F7B731"]
    )
    fig_d.update_layout(showlegend=False, **get_banking_chart_layout(f"{seg_method} Distribution", height=350))
    st.plotly_chart(fig_d, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### 👥 **Customer Drill-Down by Segment**")
selected_filter_col = "rfm_segment" if seg_method == "RFM Segmentation" else ("kmeans_segment" if seg_method == "K-Means Clustering" else ("demographic_segment" if "Demographic" in seg_method else "financial_segment"))
segment_choices = ["All"] + seg_df[selected_filter_col].unique().tolist()
picked_seg = st.selectbox(f"Filter records by {selected_filter_col}:", options=segment_choices)

filtered_drill = seg_df if picked_seg == "All" else seg_df[seg_df[selected_filter_col] == picked_seg]

st.dataframe(
    filtered_drill[[
        "customer_id", "first_name", "last_name", "age", "annual_income",
        "total_balance", "txn_frequency_12m", "recency_days", "rfm_segment", "kmeans_segment"
    ]].head(25),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "📥 Export Segment Customers (.csv)",
    data=filtered_drill.to_csv(index=False).encode("utf-8"),
    file_name=f"banksight_segment_{picked_seg.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
