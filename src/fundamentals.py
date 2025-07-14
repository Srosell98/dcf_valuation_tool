import numpy as np
import streamlit as st

def calculate_piotroski_score(ticker_obj, info):
    try:
        financials = ticker_obj.financials
        balance_sheet = ticker_obj.balance_sheet
        cashflow = ticker_obj.cashflow
        if financials.empty or balance_sheet.empty or cashflow.empty:
            return None
        if len(financials.columns) < 2:
            return None
        current_year = financials.columns[0]
        previous_year = financials.columns[1]
        score_breakdown = {}
        total_score = 0
        # PROFITABILITY CRITERIA
        net_income = financials.loc['Net Income', current_year] if 'Net Income' in financials.index else 0
        score_breakdown['positive_net_income'] = 1 if net_income > 0 else 0
        total_score += score_breakdown['positive_net_income']
        total_assets_current = balance_sheet.loc['Total Assets', current_year] if 'Total Assets' in balance_sheet.index else 1
        roa_current = net_income / total_assets_current
        score_breakdown['positive_roa'] = 1 if roa_current > 0 else 0
        total_score += score_breakdown['positive_roa']
        operating_cf = cashflow.loc['Operating Cash Flow', current_year] if 'Operating Cash Flow' in cashflow.index else 0
        score_breakdown['positive_operating_cf'] = 1 if operating_cf > 0 else 0
        total_score += score_breakdown['positive_operating_cf']
        score_breakdown['quality_of_earnings'] = 1 if operating_cf > net_income else 0
        total_score += score_breakdown['quality_of_earnings']
        # LEVERAGE, LIQUIDITY & SOURCE OF FUNDS
        long_term_debt_current = balance_sheet.loc['Long Term Debt', current_year] if 'Long Term Debt' in balance_sheet.index else 0
        long_term_debt_previous = balance_sheet.loc['Long Term Debt', previous_year] if 'Long Term Debt' in balance_sheet.index else 0
        score_breakdown['decreased_debt'] = 1 if long_term_debt_current < long_term_debt_previous else 0
        total_score += score_breakdown['decreased_debt']
        current_assets_current = balance_sheet.loc['Current Assets', current_year] if 'Current Assets' in balance_sheet.index else 0
        current_liabilities_current = balance_sheet.loc['Current Liabilities', current_year] if 'Current Liabilities' in balance_sheet.index else 1
        current_ratio_current = current_assets_current / current_liabilities_current
        current_assets_previous = balance_sheet.loc['Current Assets', previous_year] if 'Current Assets' in balance_sheet.index else 0
        current_liabilities_previous = balance_sheet.loc['Current Liabilities', previous_year] if 'Current Liabilities' in balance_sheet.index else 1
        current_ratio_previous = current_assets_previous / current_liabilities_previous
        score_breakdown['increased_current_ratio'] = 1 if current_ratio_current > current_ratio_previous else 0
        total_score += score_breakdown['increased_current_ratio']
        shares_current = info.get('sharesOutstanding', 0)
        score_breakdown['no_new_shares'] = 1
        total_score += score_breakdown['no_new_shares']
        # OPERATING EFFICIENCY
        revenue_current = financials.loc['Total Revenue', current_year] if 'Total Revenue' in financials.index else 1
        cost_of_revenue_current = financials.loc['Cost Of Revenue', current_year] if 'Cost Of Revenue' in financials.index else 0
        gross_margin_current = (revenue_current - cost_of_revenue_current) / revenue_current
        revenue_previous = financials.loc['Total Revenue', previous_year] if 'Total Revenue' in financials.index else 1
        cost_of_revenue_previous = financials.loc['Cost Of Revenue', previous_year] if 'Cost Of Revenue' in financials.index else 0
        gross_margin_previous = (revenue_previous - cost_of_revenue_previous) / revenue_previous
        score_breakdown['increased_gross_margin'] = 1 if gross_margin_current > gross_margin_previous else 0
        total_score += score_breakdown['increased_gross_margin']
        asset_turnover_current = revenue_current / total_assets_current
        total_assets_previous = balance_sheet.loc['Total Assets', previous_year] if 'Total Assets' in balance_sheet.index else 1
        asset_turnover_previous = revenue_previous / total_assets_previous
        score_breakdown['increased_asset_turnover'] = 1 if asset_turnover_current > asset_turnover_previous else 0
        total_score += score_breakdown['increased_asset_turnover']
        return {
            'total_score': total_score,
            'breakdown': score_breakdown,
            'interpretation': get_piotroski_interpretation(total_score)
        }
    except Exception as e:
        st.warning(f"Could not calculate Piotroski score: {e}")
        return None

def get_piotroski_interpretation(score):
    if score >= 8:
        return "Strong"
    elif score >= 3:
        return "Moderate"
    else:
        return "Weak"

def calculate_fundamental_metrics(ticker_obj, info):
    try:
        financials = ticker_obj.financials
        balance_sheet = ticker_obj.balance_sheet
        cashflow = ticker_obj.cashflow
        if financials.empty or balance_sheet.empty:
            return None
        current_year = financials.columns[0]
        current_price = info.get('currentPrice', 0)
        market_cap = info.get('marketCap', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        shares_outstanding = info.get('sharesOutstanding', 1)
        net_income = financials.loc['Net Income', current_year] if 'Net Income' in financials.index else 0
        total_revenue = financials.loc['Total Revenue', current_year] if 'Total Revenue' in financials.index else 0
        total_assets = balance_sheet.loc['Total Assets', current_year] if 'Total Assets' in balance_sheet.index else 0
        total_debt = balance_sheet.loc['Total Debt', current_year] if 'Total Debt' in balance_sheet.index else 0
        shareholders_equity = balance_sheet.loc['Stockholders Equity', current_year] if 'Stockholders Equity' in balance_sheet.index else 0
        operating_cf = cashflow.loc['Operating Cash Flow', current_year] if 'Operating Cash Flow' in cashflow.index else 0
        capex = abs(cashflow.loc['Capital Expenditure', current_year]) if 'Capital Expenditure' in cashflow.index else 0
        metrics = {}
        metrics['pe_ratio'] = info.get('trailingPE', 0)
        metrics['ev_ebitda'] = info.get('enterpriseToEbitda', 0)
        metrics['ev_revenue'] = enterprise_value / total_revenue if total_revenue > 0 else 0
        metrics['price_to_book'] = info.get('priceToBook', 0)
        metrics['price_to_sales'] = info.get('priceToSalesTrailing12Months', 0)
        metrics['roe'] = info.get('returnOnEquity', 0)
        metrics['roa'] = net_income / total_assets if total_assets > 0 else 0
        metrics['roic'] = net_income / (total_debt + shareholders_equity) if (total_debt + shareholders_equity) > 0 else 0
        metrics['gross_margin'] = info.get('grossMargins', 0)
        metrics['operating_margin'] = info.get('operatingMargins', 0)
        metrics['net_margin'] = net_income / total_revenue if total_revenue > 0 else 0
        metrics['fcf_yield'] = (operating_cf - capex) / market_cap if market_cap > 0 else 0
        metrics['debt_to_equity'] = info.get('debtToEquity', 0)
        metrics['current_ratio'] = info.get('currentRatio', 0)
        metrics['quick_ratio'] = info.get('quickRatio', 0)
        metrics['interest_coverage'] = info.get('interestCoverage', 0)
        metrics['asset_turnover'] = total_revenue / total_assets if total_assets > 0 else 0
        metrics['inventory_turnover'] = info.get('inventoryTurnover', 0)
        metrics['receivables_turnover'] = info.get('receivablesTurnover', 0)
        return metrics
    except Exception as e:
        st.warning(f"Could not calculate fundamental metrics: {e}")
        return None

def create_fundamental_scorecard(metrics, piotroski_data):
    if not metrics:
        return None
    def score_metric(value, metric_name, reverse=False):
        if value is None or value == 0:
            return 0
        scoring_ranges = {
            'pe_ratio': (0, 15, 25, 35),
            'ev_ebitda': (0, 10, 15, 25),
            'roe': (0, 0.1, 0.15, 0.25),
            'roa': (0, 0.05, 0.1, 0.15),
            'roic': (0, 0.1, 0.15, 0.2),
            'gross_margin': (0, 0.3, 0.5, 0.7),
            'operating_margin': (0, 0.1, 0.2, 0.3),
            'current_ratio': (0, 1.5, 2.0, 3.0),
            'debt_to_equity': (0, 0.3, 0.5, 1.0),
        }
        if metric_name in scoring_ranges:
            thresholds = scoring_ranges[metric_name]
            if metric_name in ['pe_ratio', 'ev_ebitda', 'debt_to_equity']:
                if value <= thresholds[1]:
                    return 100
                elif value <= thresholds[2]:
                    return 75
                elif value <= thresholds[3]:
                    return 50
                else:
                    return 25
            else:
                if value >= thresholds[3]:
                    return 100
                elif value >= thresholds[2]:
                    return 75
                elif value >= thresholds[1]:
                    return 50
                else:
                    return 25
        return 50
    valuation_score = np.mean([
        score_metric(metrics.get('pe_ratio', 0), 'pe_ratio'),
        score_metric(metrics.get('ev_ebitda', 0), 'ev_ebitda'),
        score_metric(metrics.get('price_to_book', 0), 'pe_ratio'),
    ])
    quality_score = np.mean([
        score_metric(metrics.get('roe', 0), 'roe'),
        score_metric(metrics.get('roa', 0), 'roa'),
        score_metric(metrics.get('roic', 0), 'roic'),
        score_metric(metrics.get('gross_margin', 0), 'gross_margin'),
        score_metric(metrics.get('operating_margin', 0), 'operating_margin'),
    ])
    strength_score = np.mean([
        score_metric(metrics.get('current_ratio', 0), 'current_ratio'),
        score_metric(metrics.get('debt_to_equity', 0), 'debt_to_equity'),
        score_metric(metrics.get('quick_ratio', 0), 'current_ratio'),
    ])
    piotroski_score = (piotroski_data['total_score'] / 9) * 100 if piotroski_data else 0
    overall_score = np.mean([valuation_score, quality_score, strength_score, piotroski_score])
    return {
        'valuation_score': valuation_score,
        'quality_score': quality_score,
        'strength_score': strength_score,
        'piotroski_score': piotroski_score,
        'overall_score': overall_score
    }
