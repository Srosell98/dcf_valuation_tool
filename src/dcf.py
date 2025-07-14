import numpy as np
import pandas as pd
from typing import Optional

def extract_free_cash_flow(cf: pd.DataFrame) -> pd.Series:
    if cf is None:
        raise ValueError("No cashflow data available.")
    if "Free Cash Flow" in cf.index:
        raw = cf.loc["Free Cash Flow"]
    else:
        ops = next((cf.loc[k] for k in ["Operating Cash Flow", "Total Cash From Operating Activities"] if k in cf.index), None)
        cap = next((cf.loc[k] for k in ["Capital Expenditure", "Investments In Property Plant And Equipment"] if k in cf.index), None)
        if ops is None or cap is None:
            raise ValueError("No FCF data.")
        raw = ops + cap
    fcf = pd.to_numeric(raw, errors="coerce").dropna().sort_index()
    fcf_pos = fcf[fcf > 0]
    if len(fcf_pos) < 2:
        raise ValueError("Not enough positive FCF.")
    return fcf_pos

def compute_historical_growth(fcf_pos: pd.Series, cap_rate: float) -> float:
    start, end = fcf_pos.iloc[0], fcf_pos.iloc[-1]
    yrs = len(fcf_pos) - 1
    g = (end / start)**(1/yrs) - 1
    return min(g, cap_rate)

def dcf_value(last_fcf: float, dr: float, term_gr: float, gr: float, n_years: int) -> float:
    years = np.arange(1, n_years + 1)
    projs = last_fcf * (1 + gr)**years
    discs = projs / (1 + dr)**years
    term_fcf = last_fcf * (1 + gr)**n_years
    term_val = term_fcf * (1 + term_gr) / (dr - term_gr)
    term_disc = term_val / (1 + dr)**n_years
    return discs.sum() + term_disc

def build_sensitivity_grid(fcf_last: float, shares: float, drs: list[float], term_grs: list[float], grs: list[float], n_years: int, current_price: float) -> dict[str, pd.DataFrame]:
    grids = {}
    for gr in grs:
        idx = [f"{d*100:.0f}%" for d in drs]
        cols = [f"{tg*100:.1f}%" for tg in term_grs]
        df = pd.DataFrame(index=idx, columns=cols, dtype=float)
        for d in drs:
            for tg in term_grs:
                if tg >= d:
                    val = np.nan
                else:
                    ev = dcf_value(fcf_last, d, tg, gr, n_years)
                    val = round(ev / shares, 2)
                df.at[f"{d*100:.0f}%", f"{tg*100:.1f}%"] = val
        grids[f"{gr:.1%}"] = df
    return grids

def build_historic_fcf_df(fcf_pos: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({
        "Year": fcf_pos.index.year,
        "Free Cash Flow": fcf_pos.values
    })

def build_projections_df(last_fcf: float, dr: float, term_gr: float, gr: float, n_years: int) -> pd.DataFrame:
    years = np.arange(1, n_years + 1)
    proj = last_fcf * (1 + gr) ** years
    disc = proj / (1 + dr) ** years
    return pd.DataFrame({
        "Year": [pd.Timestamp.today().year + int(y) for y in years],
        "Projected FCF": proj,
        "Discounted FCF": disc
    })
