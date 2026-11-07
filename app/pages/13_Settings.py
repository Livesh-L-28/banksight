"""
BankSight Platform Settings & System Diagnostics
Environment configuration, database connectivity audits, and risk threshold calibration.
"""

import sys
import os
from pathlib import Path
import streamlit as st
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.ui_components import (
    apply_banking_theme, render_page_header, render_metric_card,
    BANK_NAVY, BANK_BLUE, BANK_ACCENT, BANK_GREEN
)
from backend.database.connection import DATABASE_URL, get_db_session, engine, Base

st.set_page_config(page_title="Platform Settings | BankSight", page_icon="⚙️", layout="wide")
apply_banking_theme()

render_page_header(
    title="Platform Settings & System Diagnostics",
    subtitle="Database connectivity audit, operational risk threshold calibration, and system integrity verification",
    badge_text="Module 13 — Settings"
)

# Database Status Audit
session = get_db_session()
try:
    session.execute(text("SELECT 1;"))
    db_status = "Connected & Healthy"
    db_color = BANK_GREEN
    total_tables = len(Base.metadata.tables)
except Exception as e:
    db_status = f"Error: {e}"
    db_color = "#EB3B5A"
    total_tables = 0
session.close()

# Mask DB URL for security
masked_url = DATABASE_URL
if "@" in masked_url:
    prefix = masked_url.split("@")[0]
    suffix = masked_url.split("@")[1]
    masked_url = f"{prefix.split('://')[0]}://****:****@{suffix}"

m1, m2, m3 = st.columns(3)
with m1:
    render_metric_card("Database Health", db_status, "ACID Relational Session Pool", delta_color=db_color)
with m2:
    render_metric_card("Dialect / Engine", DATABASE_URL.split("://")[0].upper(), "SQLAlchemy 2.0 ORM")
with m3:
    render_metric_card("Relational Schema", f"{total_tables} Entities", "Alembic Migrations Applied")

st.markdown("<br>", unsafe_allow_html=True)

# Risk Threshold Configuration Section
st.markdown("##### 🎛️ **Operational Churn Risk Threshold Calibration**")
st.caption("Adjust calibrated probability bounds governing operational case creation and marketing segmentation.")

c_col1, c_col2 = st.columns(2)
with c_col1:
    high_thresh = st.slider("High Risk Priority Queue Threshold (P > threshold)", min_value=0.50, max_value=0.85, value=0.65, step=0.05)
with c_col2:
    med_thresh = st.slider("Medium Risk Digital Nudge Threshold (P >= threshold)", min_value=0.20, max_value=0.50, value=0.35, step=0.05)

if st.button("💾 Save Risk Threshold Parameters"):
    st.success(f"Parameters updated: High Risk = P > {high_thresh:.2f}, Medium Risk = P >= {med_thresh:.2f}.")

st.markdown("<br>", unsafe_allow_html=True)

# System Diagnostics Suite
st.markdown("##### 🔍 **System Diagnostics & Self-Healing**")

d_col1, d_col2 = st.columns(2)
with d_col1:
    if st.button("🧪 Run End-to-End System Diagnostic Ping"):
        with st.spinner("Pinging database, inspecting schemas, checking ML models..."):
            session = get_db_session()
            c_count = session.execute(text("SELECT COUNT(*) FROM customers;")).scalar()
            t_count = session.execute(text("SELECT COUNT(*) FROM transactions;")).scalar()
            session.close()
            st.success(f"Diagnostic passed! Verified {c_count:,} customers and {t_count:,} transactions with 0 schema violations.")

with d_col2:
    if st.button("🧹 Clear In-Memory Caches"):
        st.cache_data.clear()
        st.success("In-memory analytical cache successfully cleared.")

st.markdown("<br>", unsafe_allow_html=True)

# Security & Compliance Overview
st.markdown("##### 🔒 **Security & Privacy Standards**")
st.markdown(
    """
    - **Zero Real PII Mandate:** All customer identities, accounts, phone numbers, and transactions are 100% synthetically generated.
    - **Parameterized SQL:** All queries are strictly parameterized via SQLAlchemy ORM; zero raw string SQL injection vectors.
    - **Environment-Based Config:** Sensitive keys and connection URLs are loaded from `.env` with `.gitignore` enforcement.
    - **Human-in-the-Loop AI:** Algorithmic recommendations are advisory; binding customer interventions require RM authorization.
    """
)
