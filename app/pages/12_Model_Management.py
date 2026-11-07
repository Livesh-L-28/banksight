"""
BankSight Model Management & MLOps Studio
Model registry, version tracking, hyperparameter audit, champion-challenger benchmarks, and feature weights.
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
    get_banking_chart_layout, BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN
)
from backend.database.connection import get_db_session
from backend.models import ModelVersion
from backend.services.churn_service import ChurnService

st.set_page_config(page_title="Model Management | BankSight", page_icon="⚙️", layout="wide")
apply_banking_theme()

render_page_header(
    title="Model Governance & MLOps Management",
    subtitle="Model version registry, champion-challenger lineage, hyperparameter tracking, and feature attribution governance",
    badge_text="Module 12 — MLOps"
)

session = get_db_session()
models = session.query(ModelVersion).order_by(ModelVersion.training_date.desc()).all()
session.close()

if models:
    champ = next((m for m in models if m.is_champion), models[0])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Champion Model", champ.algorithm, "Production Deployed")
    with m2:
        render_metric_card("Champion ROC-AUC", f"{champ.roc_auc:.3f}", "Class Separation Ability")
    with m3:
        render_metric_card("Champion F1-Score", f"{champ.f1_score:.3f}", "Precision / Recall Harmonic")
    with m4:
        render_metric_card("Registered Versions", f"{len(models)}", "Audited ML Artifacts")

    st.markdown("<br>", unsafe_allow_html=True)

    # Model Registry Table
    st.markdown("##### 📦 **Registered Model Versions**")
    m_rows = [
        {
            "Model ID": m.model_id,
            "Version Tag": m.version_tag,
            "Algorithm": m.algorithm,
            "Accuracy": f"{m.accuracy:.4f}",
            "Precision": f"{m.precision:.4f}",
            "Recall": f"{m.recall:.4f}",
            "F1-Score": f"{m.f1_score:.4f}",
            "ROC-AUC": f"{m.roc_auc:.4f}",
            "Champion": "⭐ Champion" if m.is_champion else "Challenger",
            "Trained On": m.training_date.strftime("%Y-%m-%d %H:%M:%S") if m.training_date else "N/A"
        }
        for m in models
    ]
    st.dataframe(pd.DataFrame(m_rows), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Importance Weights of Champion
    if champ.feature_importances:
        st.markdown(f"##### ⚖️ **Champion Feature Importance Weights ({champ.algorithm})**")
        f_df = pd.DataFrame(list(champ.feature_importances.items()), columns=["Feature", "Importance"])
        f_df = f_df.sort_values(by="Importance", ascending=True)

        fig = px.bar(
            f_df,
            x="Importance",
            y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale=["#CBD5E1", BANK_NAVY]
        )
        fig.update_layout(**get_banking_chart_layout(f"{champ.algorithm} Relative Feature Contributions", height=320))
        st.plotly_chart(fig, use_container_width=True)

    # Retrain button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Trigger Automated Champion Re-Training"):
        with st.spinner("Retraining candidate algorithms and scoring portfolio..."):
            churn_svc = ChurnService()
            churn_svc.run_training_and_scoring(persist=True)
            st.success("Champion model retrained and updated successfully!")
            st.rerun()
else:
    st.info("No registered model versions found. Please run Churn Intelligence training first.")
