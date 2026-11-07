"""
BankSight Model Management & MLOps Studio
Includes Model Registry & Version Tracking, Federal Reserve CCAR / Basel III Stress Testing,
and Core Banking Webhook Integrations Bus.
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
from backend.database.connection import get_db_session
from backend.models import ModelVersion
from analytics.churn.retrainer import AutomatedModelRetrainer
from analytics.stress_testing.ccar_simulator import CCARStressTestSimulator
from backend.monitoring.webhooks import EnterpriseWebhookBus, WebhookEventTypes

st.set_page_config(page_title="Model Management & Risk Studio | BankSight", page_icon="⚙️", layout="wide")
apply_banking_theme()

render_page_header(
    title="Model Governance, Stress Testing & MLOps Studio",
    subtitle="Model lineage registry, Federal Reserve CCAR liquidity stress testing, and Core Banking webhook integrations",
    badge_text="Module 12 — Institutional Governance"
)

tab_registry, tab_stress, tab_webhooks = st.tabs([
    "📦 Model Registry & Lineage",
    "🏛️ Fed CCAR & Basel III Stress Testing",
    "⚡ Core Banking Webhooks Bus"
])

# ==========================================
# TAB 1: MODEL REGISTRY & LINEAGE
# ==========================================
with tab_registry:
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

        st.markdown("##### 📦 **Registered Model Versions & Champion Lineage**")
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
                "Champion Status": "⭐ Champion" if m.is_champion else "Challenger",
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

        st.markdown("<br>", unsafe_allow_html=True)
        retrain_col1, retrain_col2 = st.columns([2, 3])
        with retrain_col1:
            if st.button("🚀 Trigger Champion-Challenger Retraining Pipeline"):
                with st.spinner("Executing candidate algorithms, PSI drift assessment, and promotion checks..."):
                    result = AutomatedModelRetrainer.execute_pipeline_retraining()
                    if result["promoted_to_champion"]:
                        st.success(f"Challenger outperformed champion and was promoted! New ROC-AUC: {result['challenger_metrics']['roc_auc']:.4f}")
                    else:
                        st.info(f"Retraining completed. Challenger ({result['challenger_metrics']['roc_auc']:.4f}) did not exceed champion promotion hurdle. Kept current champion.")
                    st.rerun()
    else:
        st.info("No registered model versions found. Please run Churn Intelligence training first.")


# ==========================================
# TAB 2: FED CCAR & BASEL III STRESS TESTING
# ==========================================
with tab_stress:
    st.markdown("##### 🏛️ **Federal Reserve CCAR / DFAST & Basel III Liquidity Simulator**")
    st.caption("Simulates macroeconomic rate shocks, deposit flight velocity, and 30-day Basel III Liquidity Coverage Ratio (LCR) buffers.")

    sc_col1, sc_col2 = st.columns([1, 1])
    with sc_col1:
        selected_scenario = st.selectbox(
            "Select Supervisory Macroeconomic Scenario:",
            options=["BASELINE", "ADVERSE", "SEVERELY_ADVERSE"],
            format_func=lambda x: f"{x} — {CCARStressTestSimulator.SCENARIOS[x]['name']}"
        )
    with sc_col2:
        hqla_buffer = st.slider(
            "Available High Quality Liquid Assets (HQLA Buffer USD):",
            min_value=5_000_000,
            max_value=30_000_000,
            value=12_000_000,
            step=500_000,
            format="$%d"
        )

    # Run simulation
    sim_result = CCARStressTestSimulator.run_simulation(
        scenario_key=selected_scenario,
        custom_hqla_buffer_usd=float(hqla_buffer)
    )

    macro = sim_result["macro_assumptions"]
    impact = sim_result["portfolio_impact"]
    liquidity = sim_result["basel_iii_liquidity"]

    # Metric Banner
    sm1, sm2, sm3, sm4 = st.columns(4)
    with sm1:
        render_metric_card("Stressed Deposits", format_currency(impact["stressed_remaining_deposits_usd"]), f"Baseline: {format_currency(impact['baseline_deposits_usd'])}")
    with sm2:
        render_metric_card("Liquidity Outflow (30d)", format_currency(impact["stressed_outflow_usd"]), f"{macro['projected_outflow_pct']}% of Deposits")
    with sm3:
        lcr_status = "✅ PASS" if liquidity["lcr_compliant"] else "❌ DEFICIT"
        render_metric_card("Basel III LCR Ratio", f"{liquidity['projected_lcr_pct']:.1f}%", f"{lcr_status} (Min 100.0%)")
    with sm4:
        surplus_deficit = liquidity["hqla_surplus_deficit_usd"]
        sd_label = f"+{format_currency(surplus_deficit)}" if surplus_deficit >= 0 else format_currency(surplus_deficit)
        render_metric_card("HQLA Net Position", sd_label, "Surplus" if surplus_deficit >= 0 else "Liquidity Shortfall")

    st.markdown("<br>", unsafe_allow_html=True)

    # Gauges and Macro Table
    g_col1, g_col2 = st.columns([2, 3])
    with g_col1:
        fig_lcr = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=liquidity["projected_lcr_pct"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Basel III LCR ({selected_scenario})", 'font': {'size': 18, 'color': BANK_NAVY}},
            delta={'reference': 100.0, 'increasing': {'color': "#20BF6B"}, 'decreasing': {'color': "#EB3B5A"}},
            gauge={
                'axis': {'range': [0, 250], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#20BF6B" if liquidity["lcr_compliant"] else "#EB3B5A"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 100], 'color': '#FFECEC'},
                    {'range': [100, 250], 'color': '#EDFDF5'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100.0
                }
            }
        ))
        fig_lcr.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_lcr, use_container_width=True)

    with g_col2:
        st.markdown("##### 📋 **Macroeconomic Scenario Parameters**")
        macro_table = pd.DataFrame([
            {"Parameter": "GDP Growth Rate", "Supervisory Value": f"{macro['gdp_growth_pct']:+.1f}%"},
            {"Parameter": "Fed Funds Target Rate", "Supervisory Value": f"{macro['fed_funds_rate_pct']:.2f}%"},
            {"Parameter": "National Unemployment Rate", "Supervisory Value": f"{macro['unemployment_rate_pct']:.1f}%"},
            {"Parameter": "Deposit Beta Sensitivity", "Supervisory Value": f"{macro['deposit_beta']:.2f}"},
            {"Parameter": "30-Day Outflow Velocity", "Supervisory Value": f"{macro['projected_outflow_pct']:.1f}%"},
            {"Parameter": "Stressed Churn Attrition", "Supervisory Value": f"{impact['stressed_churn_rate_pct']:.1f}%"}
        ])
        st.dataframe(macro_table, use_container_width=True, hide_index=True)

    # Supervisory Recommendation Alert
    alert_type = st.success if liquidity["lcr_compliant"] else st.warning
    alert_type(f"**Regulatory Recommendation:** {sim_result['supervisory_recommendation']}")

    # Benchmark All Scenarios
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📊 **Multi-Scenario Supervisory Comparison**")
    all_sims = CCARStressTestSimulator.run_all_scenarios(hqla_buffer_usd=float(hqla_buffer))
    comparison_rows = [
        {
            "Scenario": s["scenario_name"],
            "GDP Growth": f"{s['macro_assumptions']['gdp_growth_pct']:+.1f}%",
            "Fed Funds": f"{s['macro_assumptions']['fed_funds_rate_pct']:.2f}%",
            "Outflow %": f"{s['macro_assumptions']['projected_outflow_pct']:.1f}%",
            "30-Day Outflow USD": format_currency(s['portfolio_impact']['stressed_outflow_usd']),
            "Remaining Deposits": format_currency(s['portfolio_impact']['stressed_remaining_deposits_usd']),
            "Projected LCR": f"{s['basel_iii_liquidity']['projected_lcr_pct']:.1f}%",
            "Compliance": "✅ PASS" if s['basel_iii_liquidity']['lcr_compliant'] else "❌ DEFICIT"
        }
        for s in all_sims
    ]
    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)


# ==========================================
# TAB 3: CORE BANKING WEBHOOKS BUS
# ==========================================
with tab_webhooks:
    st.markdown("##### ⚡ **Core Banking System Real-Time Webhooks Bus**")
    st.caption("Event delivery bus for external Core Banking platforms (FIS, Fiserv, Temenos, Finacle). Dispatches HMAC-SHA256 authenticated event envelopes.")

    subs = EnterpriseWebhookBus.list_subscriptions()
    deliveries = EnterpriseWebhookBus.get_recent_deliveries(limit=25)

    wh_m1, wh_m2, wh_m3 = st.columns(3)
    with wh_m1:
        render_metric_card("Active Webhooks", f"{len(subs)}", "Registered Endpoints")
    with wh_m2:
        render_metric_card("Recent Deliveries", f"{len(deliveries)}", "Audit Trail Events")
    with wh_m3:
        render_metric_card("Signature Standard", "HMAC-SHA256", "Cryptographically Signed")

    st.markdown("<br>", unsafe_allow_html=True)

    wh_col1, wh_col2 = st.columns([3, 2])
    with wh_col1:
        st.markdown("##### 🔌 **Configured Core Banking Webhook Endpoints**")
        if subs:
            st.dataframe(
                pd.DataFrame(subs)[[
                    "subscription_id", "target_url", "description", "subscribed_events", "created_at"
                ]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No active webhook subscriptions configured. Use the form on the right or SDK to register an endpoint.")

        # Test Dispatch Trigger
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🧪 **Trigger Synthetic Integration Event**")
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            test_event = st.selectbox("Event Type to Simulate:", options=WebhookEventTypes.ALL_EVENTS)
        with t_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Dispatch Test Event"):
                res = EnterpriseWebhookBus.dispatch_event(
                    event_type=test_event,
                    payload={"test": True, "event_source": "Streamlit_UI_Console", "customer_id": "CUST-00001"},
                    simulate_only=True
                )
                st.success(f"Dispatched {test_event} to {len(res)} subscriber(s)!")
                st.rerun()

    with wh_col2:
        st.markdown("##### ➕ **Register New Webhook Endpoint**")
        with st.form("new_webhook_form"):
            new_target_url = st.text_input("Receiver Target URL", value="https://core-banking.bank.internal/api/events")
            new_secret = st.text_input("HMAC Shared Secret Key", value="whsec_bank_enterprise_key_2026", type="password")
            new_desc = st.text_input("Description / System Name", value="Core Banking Attrition Listener")
            new_events = st.multiselect(
                "Subscribed Events",
                options=WebhookEventTypes.ALL_EVENTS,
                default=[WebhookEventTypes.CAPITAL_FLIGHT, WebhookEventTypes.CHURN_ALERT]
            )
            sub_submit = st.form_submit_button("Save & Register Webhook")
            if sub_submit:
                if new_target_url and new_secret:
                    EnterpriseWebhookBus.register_subscription(
                        target_url=new_target_url,
                        secret_key=new_secret,
                        subscribed_events=new_events,
                        description=new_desc
                    )
                    st.success("Webhook endpoint successfully registered!")
                    st.rerun()
                else:
                    st.error("Target URL and Secret Key are required.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📜 **Recent Outbound Delivery Audit Log**")
    if deliveries:
        st.dataframe(pd.DataFrame(deliveries)[[
            "delivery_id", "subscription_id", "event_type", "http_status_code",
            "delivery_status", "signature", "timestamp"
        ]], use_container_width=True, hide_index=True)
    else:
        st.info("No webhook deliveries recorded yet.")
