import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd

def apply_custom_css():
    st.markdown('''
    <style>
    /* Main background and font */
    .main, body, .block-container {
        background-color: #232936 !important;
        color: #e0e6ed !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #232936 !important;
        color: #e0e6ed !important;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #232936 !important;
        font-weight: bold !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        background-color: #181c24 !important;
        color: #232936 !important;
        border: 1px solid #394867 !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }
    .stButton > button {
        background-color: #1976d2;
        color: #fff;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1565c0 !important;
        color: #fff !important;
        box-shadow: 0 2px 8px rgba(30,136,229,0.25);
    }
    .container-header::after,
    .parameter-section .container-header::after,
    .container-header > span.bubble-icon {
        content: none !important;
        display: none !important;
    }
    .parameter-section, .container-header, .card.parameter-section {
        background-color: #181c24 !important;
        color: #fff !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.20);
    }
    .container-header {
        border-left: 4px solid #FF1744 !important;
        color: #fff !important;
        font-weight: bold !important;
        letter-spacing: 0.5px;
        padding: 8px 0 8px 12px;
        margin-bottom: 10px;
        font-size: 1.1rem;
    }
    .parameter-section input,
    .parameter-section select,
    .parameter-section textarea {
        background-color: #232936 !important;
        color: #232936 !important;
        border: 1px solid #1a237e !important;
    }
    .current-price-bubble {
        background-color: #181c24 !important;
        color: #181c24 !important;
        border: 1px solid #181c24 !important;
        border-radius: 16px !important;
        padding: 4px 12px !important;
        font-weight: bold !important;
        display: inline-block !important;
    }
    .card {
        border-radius: 10px;
        background-color: #181c24;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        padding: 20px;
        margin-bottom: 20px;
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #394867;
        background-color: #181c24 !important;
        color: #e0e6ed !important;
        padding: 10px;
    }
    .stSlider > div > div {
        color: #90caf9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #181c24;
        color: #b0bec5;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976d2 !important;
        color: #fff !important;
        font-weight: bold !important;
    }
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #90caf9;
        background-color: #181c24;
        border-radius: 5px;
    }
    div[data-baseweb="tooltip"] {
        background-color: #181c24;
        color: #e0e6ed;
        border-radius: 5px;
        padding: 10px;
        font-size: 0.9rem;
    }
    @media (max-width: 768px) {
        .card {
            padding: 15px;
        }
        .stButton > button {
            width: 100%;
        }
    }
    .metric-container {
        display: flex;
        align-items: center;
        background-color: #232936;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.25);
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #90caf9;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #b0bec5;
        margin-top: -5px;
    }
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
        border-radius: 10px;
        overflow: hidden;
        background-color: #232936;
        color: #e0e6ed;
    }
    .styled-table thead tr {
        background-color: #1976d2;
        color: #ffffff;
        text-align: left;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #394867;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #181c24;
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid #1976d2;
    }
    .indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .indicator-positive {
        background-color: #a6d7a8;
    }
    .indicator-negative {
        background-color: #faa19a;
    }
    .indicator-neutral {
        background-color: #ffe083;
    }
    </style>
    ''', unsafe_allow_html=True)

def create_metric_card(label, value, delta=None, prefix="", suffix=""):
    delta_html = ""
    if delta is not None:
        color = "green" if delta >= 0 else "red"
        arrow = "↑" if delta >= 0 else "↓"
        delta_html = f'<span style="color:{color};font-size:1rem;margin-left:5px;">{arrow} {abs(delta):.1f}%</span>'
    html = f"""
    <div style="background-color:#181c24;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1);padding:15px;margin-bottom:15px;">
        <div style="font-size:0.9rem;color:#fff;">{label}</div>
        <div style="font-size:1.8rem;font-weight:700;color:#1E88E5;">{prefix}{value}{suffix}{delta_html}</div>
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def style_sensitivity_table(df: pd.DataFrame, current_price: float) -> pd.DataFrame:
    def color_value(val):
        if pd.isna(val):
            return 'background-color: #b0bec5; color: #232936;'
        elif val > current_price * 1.2:
            return 'background-color: #81c784; color: #232936; font-weight: bold;'
        elif val > current_price:
            return 'background-color: #b3e5fc; color: #232936;'
        elif val > current_price * 0.8:
            return 'background-color: #ffe082; color: #232936;'
        else:
            return 'background-color: #ff8a80; color: #232936;'
    return df.style.format("{:.2f}").applymap(color_value)

def format_table_for_display(df: pd.DataFrame) -> pd.DataFrame:
    df_formatted = df.copy()
    if "Year" in df_formatted.columns:
        df_formatted["Year"] = df_formatted["Year"].astype(str)
    return df_formatted

def create_technical_metric_card(label, value, status, color):
    st.markdown(f"""
    <div style="background-color: #181c24; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; margin-bottom: 15px; border-left: 4px solid {color};">
        <div style="font-size: 0.9rem; color: #e0e6ed; margin-bottom: 5px;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1E88E5; margin-bottom: 5px;">{value}</div>
        <div style="font-size: 0.8rem; color: {color}; font-weight: 500;">{status}</div>
    </div>
    """, unsafe_allow_html=True)


def create_score_gauge(title, score):
    """Create a circular gauge for scores"""
    color = get_gauge_color(score)
    st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <div style="
            width: 80px; height: 80px; 
            border-radius: 50%; 
            background: conic-gradient({color} {score*3.6}deg, #e0e0e0 0deg);
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 10px auto;
        ">
            <div style="
                width: 60px; height: 60px; 
                border-radius: 50%; 
                background: #232936;
                display: flex; align-items: center; justify-content: center;
                color: white; font-weight: bold;
            ">
                {int(score)}
            </div>
        </div>
        <div style="color: #e0e6ed; font-size: 0.9rem;">{title}</div>
    </div>
    """, unsafe_allow_html=True)

def get_gauge_color(score):
    if score >= 80:
        return "#4CAF50"  # Green
    elif score >= 60:
        return "#FF9800"  # Orange
    elif score >= 40:
        return "#FFC107"  # Yellow
    else:
        return "#F44336"  # Red

def get_score_color(score):
    if score >= 8:
        return "#4CAF50"  # Green
    elif score >= 6:
        return "#FF9800"  # Orange
    elif score >= 4:
        return "#FFC107"  # Yellow
    else:
        return "#F44336"  # Red

def display_fundamental_analysis(ticker, metrics, piotroski_data, scorecard):
    """
    Display comprehensive fundamental analysis in Streamlit
    """
    st.markdown('<div class="container-header">Fundamental Analysis Dashboard</div>', unsafe_allow_html=True)
    if scorecard:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            create_score_gauge("Overall", scorecard['overall_score'])
        with col2:
            create_score_gauge("Valuation", scorecard['valuation_score'])
        with col3:
            create_score_gauge("Quality", scorecard['quality_score'])
        with col4:
            create_score_gauge("Strength", scorecard['strength_score'])
        with col5:
            create_score_gauge("Piotroski", scorecard['piotroski_score'])
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Valuation Metrics", "⭐ Quality & Profitability", "🛡️ Balance Sheet Strength", "🎯 Piotroski F-Score"])
    with tab1:
        if metrics:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Relative Valuation")
                create_metric_card("P/E Ratio", f"{metrics.get('pe_ratio', 0):.2f}")
                create_metric_card("EV/EBITDA", f"{metrics.get('ev_ebitda', 0):.2f}")
                create_metric_card("Price/Book", f"{metrics.get('price_to_book', 0):.2f}")
            with col2:
                st.subheader("Market Multiples")
                create_metric_card("Price/Sales", f"{metrics.get('price_to_sales', 0):.2f}")
                create_metric_card("EV/Revenue", f"{metrics.get('ev_revenue', 0):.2f}")
                create_metric_card("FCF Yield", f"{metrics.get('fcf_yield', 0):.2%}")
    with tab2:
        if metrics:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Profitability")
                create_metric_card("ROE", f"{metrics.get('roe', 0):.2%}")
                create_metric_card("ROA", f"{metrics.get('roa', 0):.2%}")
                create_metric_card("ROIC", f"{metrics.get('roic', 0):.2%}")
            with col2:
                st.subheader("Margins")
                create_metric_card("Gross Margin", f"{metrics.get('gross_margin', 0):.2%}")
                create_metric_card("Operating Margin", f"{metrics.get('operating_margin', 0):.2%}")
                create_metric_card("Net Margin", f"{metrics.get('net_margin', 0):.2%}")
    with tab3:
        if metrics:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Liquidity")
                create_metric_card("Current Ratio", f"{metrics.get('current_ratio', 0):.2f}")
                create_metric_card("Quick Ratio", f"{metrics.get('quick_ratio', 0):.2f}")
            with col2:
                st.subheader("Leverage")
                create_metric_card("Debt/Equity", f"{metrics.get('debt_to_equity', 0):.2f}")
                create_metric_card("Interest Coverage", f"{metrics.get('interest_coverage', 0):.2f}")
    with tab4:
        if piotroski_data:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Piotroski F-Score")
                score_color = get_score_color(piotroski_data['total_score'])
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: {score_color}; border-radius: 10px; margin: 10px 0;">
                    <h1 style="color: white; margin: 0;">{piotroski_data['total_score']}/9</h1>
                    <p style="color: white; margin: 0;">{piotroski_data['interpretation']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.subheader("Score Breakdown")
                breakdown = piotroski_data['breakdown']
                categories = {
                    'Profitability': ['positive_net_income', 'positive_roa', 'positive_operating_cf', 'quality_of_earnings'],
                    'Leverage & Liquidity': ['decreased_debt', 'increased_current_ratio', 'no_new_shares'],
                    'Operating Efficiency': ['increased_gross_margin', 'increased_asset_turnover']
                }
                for category, items in categories.items():
                    st.write(f"**{category}:**")
                    for item in items:
                        score = breakdown.get(item, 0)
                        icon = "✅" if score == 1 else "❌"
                        st.write(f"{icon} {item.replace('_', ' ').title()}: {score}")
                    st.write("")

def create_loading_spinner():
    st.spinner("Loading...")  # This will show a spinner while the app is loading
    st.session_state.loading = True