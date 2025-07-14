import yfinance as yf
import streamlit as st
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def fetch_financials(ticker: str):
    try:
        st.session_state.loading = True
        with st.spinner(f"Fetching data for {ticker}..."):
            tk = yf.Ticker(ticker)
            cf = tk.cashflow
            inc_stmt = tk.financials
            bal_sheet = tk.balance_sheet
            info = tk.info
        st.session_state.loading = False
        return cf, inc_stmt, bal_sheet, info
    except Exception as e:
        st.session_state.loading = False
        st.error(f"Error fetching data for {ticker}: {e}")
        return None, None, None, None
