"""
BankSight Transaction Analytics Studio
Channel dynamics, spending pattern breakdown, dormant account alerts, and ledger reconciliation checks.
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
from backend.services.transaction_service import TransactionService

st.set_page_config(page_title="Transaction Analytics | BankSight", page_icon="💳", layout="wide")
apply_banking_theme()

render_page_header(
    title="Transaction Analytics & Ledger Reconciliation",
    subtitle="Omnichannel payment flows, consumer expenditure trends, dormancy detection, and analytical reconciliation audits",
    badge_text="Module 6 — Transaction Analytics"
)

txn_service = TransactionService()

# Run reconciliation audit
recon = txn_service.run_reconciliation()

# Top Reconciliation Row
r1, r2, r3, r4, r5 = st.columns(5)
with r1:
    render_metric_card("Total Ledger Records", f"{recon['total_transaction_records']:,}", "ACID Completed Txns")
with r2:
    render_metric_card("Total Deposits", format_currency(recon["total_deposit_amount"]), "Inbound Liquidity")
with r3:
    render_metric_card("Total Withdrawals", format_currency(recon["total_withdrawal_amount"]), "Spend & Outbound Debits")
with r4:
    render_metric_card("Net Cashflow", format_currency(recon["net_flow"]), "Net Inflow / Outflow")
with r5:
    render_metric_card("Audit Status", recon["reconciliation_status"], "0 Duplicates • 0 Negatives", delta_color=BANK_GREEN)

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row 1: Channel Distribution & Spend Categories
c_col1, c_col2 = st.columns([1, 1])

with c_col1:
    st.markdown("##### 📱 **Transaction Volume by Channel**")
    channels = txn_service.get_channel_analytics()
    if channels:
        ch_df = pd.DataFrame(channels)
        fig_ch = px.pie(
            ch_df,
            names="channel",
            values="total_volume",
            hole=0.55,
            color="channel",
            color_discrete_map={
                "MOBILE": BANK_NAVY,
                "ONLINE": BANK_BLUE,
                "POS": BANK_ACCENT,
                "ATM": "#F7B731",
                "BRANCH": "#20BF6B"
            }
        )
        fig_ch.update_layout(**get_banking_chart_layout("Channel Share by Dollar Volume", height=340))
        st.plotly_chart(fig_ch, use_container_width=True)

with c_col2:
    st.markdown("##### 🛒 **Consumer Spending by Merchant Category**")
    spend = txn_service.get_spending_breakdown()
    if spend:
        sp_df = pd.DataFrame(spend)
        fig_sp = px.bar(
            sp_df,
            x="total_spend",
            y="category",
            orientation="h",
            color="total_spend",
            color_continuous_scale=["#CBD5E1", BANK_NAVY],
            labels={"total_spend": "Total Spend ($)", "category": "Category"}
        )
        fig_sp.update_layout(
            yaxis=dict(autorange="reversed"),
            **get_banking_chart_layout("Expenditure by Category", height=340)
        )
        st.plotly_chart(fig_sp, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Dormant Accounts Identification Section
st.markdown("##### 💤 **Dormant & Inactive Account Early Warning (>90 Days Inactive)**")
dormant_accounts = txn_service.get_dormant_accounts(days_threshold=90)

if dormant_accounts:
    d_df = pd.DataFrame(dormant_accounts)
    st.dataframe(
        d_df.rename(columns={
            "account_id": "Account ID",
            "account_number": "Account #",
            "customer_id": "Customer ID",
            "customer_name": "Customer Name",
            "email": "Email",
            "current_balance": "Current Balance ($)",
            "last_transaction_date": "Last Transaction Date",
            "days_inactive": "Days Inactive"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.download_button(
        "📥 Export Dormant Accounts List (.csv)",
        data=d_df.to_csv(index=False).encode("utf-8"),
        file_name="banksight_dormant_accounts.csv",
        mime="text/csv"
    )
else:
    st.success("No active accounts currently exceed the 90-day dormancy threshold.")

