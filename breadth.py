import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

def get_market_breadth(days: int = 365) -> Optional[pd.DataFrame]:
    """
    Return a DataFrame with Advancing, Declining, NetAdv and a cumulative ADLine.
    Tries three data sources in order; returns None if all fail.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    # ---------- 1) Primary: ^ADV / ^DECL from Yahoo ---------------------------
    try:
        adv = yf.download("^ADV", start, end, progress=False)["Close"]
        dec = yf.download("^DECL", start, end, progress=False)["Close"]
        if adv.size and dec.size:
            net = adv - dec
            return _package(adv, dec, net, "Yahoo (^ADV/^DECL)")
    except Exception:
        pass

    # ---------- 2) Secondary: NYSE $ADD index via TradingView  ----------------
    try:
        add = yf.download("USI:ADD", start, end, progress=False)["Close"]
        if add.size:
            # $ADD is already Net Advances; derive A/D line
            ad_line = add.cumsum()
            return pd.DataFrame({"ADLine": ad_line, "Source": "TradingView ($ADD)"})
    except Exception:
        pass

    # ---------- 3) Tertiary: Synthetic breadth from major indices ------------
    try:
        return _synthetic_breadth(start, end)
    except Exception:
        pass

    return None


def _synthetic_breadth(start, end):
    """Proxy breadth: +1 if daily return >0 else -1 for each index, averaged."""
    indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
    signals = []
    for tkr in indices:
        prices = yf.download(tkr, start, end, progress=False)["Close"]
        if prices.size:
            daily = prices.pct_change().fillna(0)
            signals.append(np.where(daily > 0, 1, -1))
    if not signals:
        raise ValueError("No proxy data")
    avg = np.mean(signals, axis=0)
    ad_ln = pd.Series(avg, index=prices.index).cumsum()
    return pd.DataFrame({"ADLine": ad_ln, "Source": "Synthetic (Idx)"})

def _package(adv, dec, net, label):
    ad_line = net.cumsum()
    return pd.DataFrame(
        {"Advancing": adv, "Declining": dec, "NetAdv": net,
         "ADLine": ad_line, "Source": label}
    )
