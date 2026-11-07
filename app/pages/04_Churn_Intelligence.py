"""
BankSight Machine Learning Churn Intelligence Studio
Trains, benchmarks, and explains predictive models with calibrated probabilities and feature attributions.
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
    format_currency, get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN, BANK_RED
)
from backend.services.churn_service import ChurnService
from backend.services.customer_service import CustomerService

st.set_page_config(page_title="Churn Intelligence | BankSight", page_icon="🎯", layout="wide")
apply_banking_theme()

render_page_header(
    title="Customer Churn Intelligence & Predictive Machine Learning",
    subtitle="Multi-model benchmarking, probability calibration, risk tier categorization, and explainable feature attributions",
    badge_text="Module 4 — Predictive ML"
)

churn_service = ChurnService()

# Controls
c_col1, c_col2 = st.columns([3, 1])
with c_col1:
    st.markdown("Automated retraining executes an 80/20 stratified split with zero future leakage, benchmarking Logistic Regression, Random Forest, and Gradient Boosting.")
with c_col2:
    retrain_clicked = st.button("🚀 Retrain & Benchmark Models", use_container_width=True)

# Run or load training results
with st.spinner("Executing machine learning training and calibration pipeline..."):
    results = churn_service.run_training_and_scoring(persist=retrain_clicked)

benchmarks = results["benchmark_results"]
champ_name = results["champion_model_name"]
risk_dist = pd.DataFrame(results["risk_distribution"])

# Model Benchmark Metrics Table
st.markdown("##### 🏆 **Model Performance Benchmark Comparison**")

benchmark_rows = []
for k, m in benchmarks.items():
    is_champ = (k == champ_name)
    benchmark_rows.append({
        "Model Algorithm": f"{'⭐ ' if is_champ else ''}{m['algorithm']}",
        "ROC-AUC Score": m["roc_auc"],
        "F1-Score": m["f1_score"],
        "Precision": m["precision"],
        "Recall": m["recall"],
        "Accuracy": m["accuracy"],
        "Champion Status": "Champion ⭐" if is_champ else "Challenger"
    })

bench_df = pd.DataFrame(benchmark_rows)
st.dataframe(bench_df, use_container_width=True, hide_index=True)

# Top metric summary cards
b1, b2, b3, b4 = st.columns(4)
champ_metrics = benchmarks[champ_name]
with b1:
    render_metric_card("Champion Model", champ_metrics["algorithm"], "Highest Discriminative AUC")
with b2:
    render_metric_card("ROC-AUC Score", f"{champ_metrics['roc_auc']:.3f}", "Class Separation Ability")
with b3:
    render_metric_card("Model Recall", f"{champ_metrics['recall']:.1%}", "At-Risk Detection Rate")
with b4:
    render_metric_card("Model F1-Score", f"{champ_metrics['f1_score']:.3f}", "Harmonic Precision-Recall")

st.markdown("<br>", unsafe_allow_html=True)

# Visual Comparison: ROC Curves & Feature Importance
v1, v2 = st.columns([1, 1])

with v1:
    st.markdown("##### 📈 **Receiver Operating Characteristic (ROC) Comparison**")
    fig_roc = go.Figure()
    fig_roc.add_shape(type="line", line=dict(dash="dash", color="#CBD5E1"), x0=0, x1=1, y0=0, y1=1)

    colors = {"logistic_regression": "#64748B", "random_forest": BANK_BLUE, "gradient_boosting": BANK_ACCENT}
    for k, m in benchmarks.items():
        fig_roc.add_trace(go.Scatter(
            x=m["roc_curve"]["fpr"],
            y=m["roc_curve"]["tpr"],
            name=f"{m['algorithm']} (AUC: {m['roc_auc']:.2f})",
            mode="lines",
            line=dict(color=colors.get(k, BANK_NAVY), width=3 if k == champ_name else 2)
        ))
    fig_roc.update_layout(**get_banking_chart_layout("ROC Curve Comparison", height=340))
    st.plotly_chart(fig_roc, use_container_width=True)

with v2:
    st.markdown("##### ⚖️ **Champion Feature Importance (Top Churn Drivers)**")
    feat_imp = pd.DataFrame(list(champ_metrics["feature_importances"].items()), columns=["Feature", "Importance"])
    feat_imp = feat_imp.sort_values(by="Importance", ascending=True)

    fig_imp = px.bar(
        feat_imp,
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance",
        color_continuous_scale=["#CBD5E1", BANK_NAVY]
    )
    fig_imp.update_layout(**get_banking_chart_layout("Feature Importance Weights", height=340))
    st.plotly_chart(fig_imp, use_container_width=True)

# Scored Customers List
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### 🎯 **Customer Churn Risk Scoring Queue**")

scored_sample = results["scored_customers_sample"]

f_col1, f_col2 = st.columns([1, 2])
with f_col1:
    filter_tier = st.selectbox("Filter Risk Category:", options=["All", "High Risk", "Medium Risk", "Low Risk"], index=1)

display_sample = scored_sample if filter_tier == "All" else scored_sample[scored_sample["risk_category"] == filter_tier]

table_rows = []
for _, r in display_sample.head(30).iterrows():
    factors_str = "; ".join(r["top_churn_factors"]) if isinstance(r["top_churn_factors"], list) else str(r["top_churn_factors"])
    table_rows.append({
        "Customer ID": r["customer_id"],
        "Full Name": f"{r['first_name']} {r['last_name']}",
        "Age": r["age"],
        "Total Balance ($)": f"${r['total_balance']:,.2f}",
        "Churn Probability": f"{r['churn_probability']:.1%}",
        "Risk Category": r["risk_category"],
        "Primary Contributing Factors": factors_str,
        "Advisory Retention Action": r["recommended_action"]
    })

st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

if st.button("🛡️ Open Retention Management Queue"):
    st.switch_page("pages/05_Retention_Management.py")

