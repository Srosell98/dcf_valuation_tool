import pandas_ta as ta
import streamlit as st
import numpy as np
import pandas as pd

def add_sma_cross_weekly(df):
    try:
        if 'Close' not in df.columns:
            st.error("❌ No 'Close' column found for SMA calculation")
            return df
        df["SMA10"] = ta.sma(df["Close"], length=10)
        df["SMA40"] = ta.sma(df["Close"], length=40)
        df["Cross"] = np.where(df["SMA10"] > df["SMA40"], 1, 0)
        return df
    except Exception as e:
        st.error(f"❌ Error calculating weekly SMA: {e}")
        return df

def add_rsi_weekly(df, length=14):
    try:
        if 'Close' not in df.columns:
            st.error("❌ No 'Close' column found for RSI calculation")
            return df
        df[f"RSI{length}"] = ta.rsi(df["Close"], length=length)
        return df
    except Exception as e:
        st.error(f"❌ Error calculating weekly RSI: {e}")
        return df

def add_macd_weekly(df):
    try:
        if 'Close' not in df.columns:
            st.error("❌ No 'Close' column found for MACD calculation")
            return df
        macd_result = ta.macd(df["Close"], fast=12, slow=26, signal=9)
        if macd_result is not None and not macd_result.empty:
            df = pd.concat([df, macd_result], axis=1)
            if 'MACD_12_26_9' in df.columns and 'MACDs_12_26_9' in df.columns:
                df["MACD_Cross"] = np.sign(df["MACD_12_26_9"] - df["MACDs_12_26_9"])
        else:
            st.error("❌ Weekly MACD calculation failed")
        return df
    except Exception as e:
        st.error(f"❌ Error calculating weekly MACD: {e}")
        return df
