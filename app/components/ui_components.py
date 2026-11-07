"""
BankSight Enterprise UI Component Library
Deep navy banking visual styling, custom HTML cards, metric indicators, and Plotly templates.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional


BANK_NAVY = "#0B192C"
BANK_BLUE = "#1E3E62"
BANK_ACCENT = "#00ADB5"
BANK_GOLD = "#F7B731"
BANK_GREEN = "#20BF6B"
BANK_RED = "#EB3B5A"
BANK_GRAY = "#F8F9FA"
BANK_BORDER = "#E2E8F0"


def apply_banking_theme():
    """Injects custom enterprise CSS for a deep navy, polished banking interface."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .main-header {{
            background: linear-gradient(135deg, {BANK_NAVY} 0%, {BANK_BLUE} 100%);
            color: white;
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px rgba(11, 25, 44, 0.15);
        }}

        .main-header h1 {{
            color: #FFFFFF !important;
            font-size: 26px;
            font-weight: 700;
            margin: 0 0 6px 0;
            letter-spacing: -0.5px;
        }}

        .main-header p {{
            color: #CBD5E1;
            font-size: 14px;
            margin: 0;
            font-weight: 400;
        }}

        .metric-card {{
            background: #FFFFFF;
            border: 1px solid {BANK_BORDER};
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            border-color: {BANK_ACCENT};
        }}

        .metric-card .title {{
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}

        .metric-card .value {{
            font-size: 24px;
            font-weight: 700;
            color: {BANK_NAVY};
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }}

        .metric-card .subtext {{
            font-size: 12px;
            color: #94A3B8;
        }}

        .badge-low {{
            background-color: #DEF7EC;
            color: #03543F;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge-med {{
            background-color: #FEF08A;
            color: #713F12;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge-high {{
            background-color: #FDE8E8;
            color: #9B1C1C;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}

        .stButton>button {{
            background-color: {BANK_NAVY} !important;
            color: white !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            border: none !important;
        }}

        .stButton>button:hover {{
            background-color: {BANK_BLUE} !important;
            box-shadow: 0 4px 12px rgba(30, 62, 98, 0.3) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_page_header(title: str, subtitle: str, badge_text: str = "Enterprise Banking Analytics"):
    """Renders standardized top banner header."""
    st.markdown(
        f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
                <div style="background: rgba(255, 255, 255, 0.15); padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; letter-spacing: 0.5px;">
                    {badge_text}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(title: str, value: str, subtext: str = "", delta_color: str = "#20BF6B"):
    """Renders an enterprise styled metric KPI card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="title">{title}</div>
            <div class="value">{value}</div>
            <div class="subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_currency(val: float) -> str:
    """Formats numeric values into standard USD currency string ($M, $K, or full)."""
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif abs(val) >= 1_000:
        return f"${val / 1_000:.1f}K"
    else:
        return f"${val:,.2f}"


def get_banking_chart_layout(title: str = "", height: int = 380) -> Dict[str, Any]:
    """Returns standardized Plotly layout dictionary matching deep navy branding."""
    return dict(
        title=dict(text=title, font=dict(family="Inter", size=14, color=BANK_NAVY, weight="bold")),
        height=height,
        margin=dict(l=40, r=30, t=50, b=40),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter", size=12, color="#475569"),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
