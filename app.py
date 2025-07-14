import streamlit as st
from src.data import fetch_financials
from src.dcf import *
from src.technicals import *
from src.fundamentals import *
from src.visuals import *
from src.ui import *
from src.utils import *
from src.config import *
import yfinance as yf
from breadth import get_market_breadth
from typing import Optional
import numpy as np

# Main analysis and Streamlit wiring

def main(
    ticker: str,
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
    terminal_growth_rate: float = DEFAULT_TERMINAL_GROWTH,
    projection_years: int = DEFAULT_PROJECTION_YEARS,
    growth_override: Optional[float] = None,
    use_override: bool = False,
    delta_dr: float = 0.02,
    delta_tg: float = 0.01,
    delta_gr: float = 0.05,
):
    try:
        cf, inc, bal, info = fetch_financials(ticker)
        if cf is None or inc is None or bal is None or info is None:
            st.error(f"Failed to fetch complete data for {ticker}")
            return None
        ticker_obj = yf.Ticker(ticker)
        # Technicals
        try:
            st.info("📊 Downloading price data...")
            price_df = yf.download(ticker, period="5y", interval="1wk", progress=False, multi_level_index=False)
            if price_df.empty:
                st.error(f"❌ No price data available for {ticker}")
                price_df = None
                breadth_data = None
            else:
                st.info("🔧 Calculating technical indicators...")
                price_df = add_sma_cross_weekly(price_df)
                price_df = add_rsi_weekly(price_df)
                price_df = add_macd_weekly(price_df)
                try:
                    breadth_data = get_market_breadth()
                except Exception as e:
                    st.warning(f"⚠️ Could not fetch breadth data: {e}")
                    breadth_data = None
                st.success("✅ Technical analysis calculations complete")
        except Exception as e:
            st.error(f"❌ Could not fetch technical analysis data: {e}")
            price_df = None
            breadth_data = None
        # Fundamentals
        fundamental_metrics = calculate_fundamental_metrics(ticker_obj, info)
        piotroski_data = calculate_piotroski_score(ticker_obj, info)
        scorecard = create_fundamental_scorecard(fundamental_metrics, piotroski_data)
        fcf_pos = extract_free_cash_flow(cf)
        last_fcf = fcf_pos.iloc[-1]
        yahoo_growth, growth_source = (info.get('revenueGrowth'), 'Revenue Growth') if info.get('revenueGrowth') else (None, None)
        hist_growth = compute_historical_growth(fcf_pos, discount_rate - delta_dr)
        if use_override and growth_override is not None:
            gr_base = growth_override
            growth_source_text = "Manual Override"
        elif yahoo_growth is not None:
            gr_base = yahoo_growth
            growth_source_text = growth_source
        else:
            gr_base = hist_growth
            growth_source_text = "Historical CAGR"
        ent_val = dcf_value(last_fcf, discount_rate, terminal_growth_rate, gr_base, projection_years)
        shares = info.get("sharesOutstanding")
        price = info.get("currentPrice")
        vps = ent_val / shares
        mos = (vps - price) / price * 100
        df_hist = build_historic_fcf_df(fcf_pos)
        df_proj = build_projections_df(last_fcf, discount_rate, terminal_growth_rate, gr_base, projection_years)
        dr_sens = list(np.arange(discount_rate - delta_dr, discount_rate + delta_dr + 1e-9, delta_dr))
        tg_sens = list(np.arange(terminal_growth_rate - delta_tg, terminal_growth_rate + delta_tg + 1e-9, delta_tg))
        gr_sens = list(np.arange(gr_base - delta_gr, gr_base + delta_gr + 1e-9, delta_gr))
        sens = build_sensitivity_grid(last_fcf, shares, dr_sens, tg_sens, gr_sens, projection_years, price)
        hist_chart = create_historical_fcf_chart(df_hist)
        proj_chart = create_projected_fcf_chart(df_proj)
        return {
            "fcf_series": fcf_pos,
            "hist_growth": hist_growth,
            "yahoo_growth": yahoo_growth,
            "growth_source": growth_source_text,
            "chosen_growth": gr_base,
            "enterprise_value": ent_val,
            "shares": shares,
            "price": price,
            "value_per_share": vps,
            "margin_of_safety": mos,
            "historic_fcf_df": df_hist,
            "projections_df": df_proj,
            "sensitivity": sens,
            "hist_chart": hist_chart,
            "proj_chart": proj_chart,
            "info": info,
            'fundamental_metrics': fundamental_metrics,
            'piotroski_data': piotroski_data,
            'scorecard': scorecard,
            'price_df': price_df,
            'breadth_data': breadth_data,
        }
    except Exception as e:
        st.error(f"Error analyzing {ticker}: {e}")
        return None

# Create the Streamlit app
def app():
    # Set page configuration
    st.set_page_config(
        page_title="DCF Valuation Tool",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state for loading indicator
    if 'loading' not in st.session_state:
        st.session_state.loading = False
    
    # Header section with logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown(
            '<div style="font-size: 10rem; line-height: 1; text-align: center;">📈</div>',
            unsafe_allow_html=True
        )
    with col2:
        st.title("Discounted Cash Flow (DCF) Valuation Tool")
        st.markdown("Evaluate stock fair value using DCF analysis")
    
    # Sidebar - Input Parameters
    with st.sidebar:
        st.markdown('<div class="container-header">Input Parameters</div>', unsafe_allow_html=True)
        
        # Stock selection container
        with st.container():
            ticker = st.text_input(
                "Ticker Symbol",
                value="AAPL",
                help="Enter the stock ticker symbol (e.g., AAPL for Apple)"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Financial parameters container
        st.markdown('<div class="container-header">DCF Model Parameters</div>', unsafe_allow_html=True)
        with st.container():            
            # Main parameters with tooltips
            discount_rate = st.slider(
                "Discount Rate (WACC)",
                min_value=0.05,
                max_value=0.20,
                value=0.08,
                step=0.01,
                format="%.2f",
                help="Weighted Average Cost of Capital - the required rate of return for the investment"
            )
            
            terminal_growth_rate = st.slider(
                "Terminal Growth Rate",
                min_value=0.01,
                max_value=0.05,
                value=0.03,
                step=0.005,
                format="%.3f",
                help="Expected long-term growth rate after the projection period"
            )
            
            projection_years = st.slider(
                "Projection Years",
                min_value=3,
                max_value=10,
                value=5,
                step=1,
                help="Number of years to project future cash flows"
            )
            
            # Collapsible advanced settings
            with st.expander("Advanced Settings"):
                delta_dr = st.slider(
                    "Discount Rate Range (±)",
                    min_value=0.01,
                    max_value=0.05,
                    value=0.02,
                    step=0.01,
                    format="%.2f",
                    help="Range for sensitivity analysis of discount rate"
                )
                
                delta_tg = st.slider(
                    "Terminal Growth Range (±)",
                    min_value=0.005,
                    max_value=0.02,
                    value=0.01,
                    step=0.005,
                    format="%.3f",
                    help="Range for sensitivity analysis of terminal growth rate"
                )
                
                delta_gr = st.slider(
                    "Growth Rate Range (±)",
                    min_value=0.01,
                    max_value=0.10,
                    value=0.05,
                    step=0.01,
                    format="%.2f",
                    help="Range for sensitivity analysis of growth rate"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Growth rate section
        st.markdown('<div class="container-header">Growth Rate Settings</div>', unsafe_allow_html=True)
        with st.container():            
            use_override = st.checkbox(
                "Use Custom Growth Rate",
                help="Override automatic growth rate calculation with a custom value"
            )
            
            growth_override = st.slider(
                "Custom Growth Rate",
                min_value=0.00,
                max_value=0.30,
                value=0.15,
                step=0.01,
                format="%.2f",
                disabled=not use_override,
                help="Custom annual growth rate for cash flow projections"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Calculate button
        calculate_btn = st.button(
            "Calculate DCF Value",
            use_container_width=True,
            help="Run the DCF analysis with the current parameters"
        )
        
        # About section at the bottom of sidebar
        with st.expander("About DCF Analysis"):
            st.markdown("""
            **Discounted Cash Flow (DCF)** analysis estimates the value of an investment based on its expected future cash flows.
            
            The method:
            1. Projects future free cash flows
            2. Applies a discount rate to determine present value
            3. Adds a terminal value for cash flows beyond the projection period
            4. Divides by shares outstanding to get per-share value
            """)
    
    # Main content area
    if calculate_btn:
        with st.spinner("Calculating..."):
            results = main(
                ticker=ticker.upper(),
                discount_rate=discount_rate,
                terminal_growth_rate=terminal_growth_rate,
                projection_years=projection_years,
                growth_override=growth_override if use_override else None,
                use_override=use_override,
                delta_dr=delta_dr,
                delta_tg=delta_tg,
                delta_gr=delta_gr
            )
            
            if results:
                st.session_state.results = results
                st.session_state.ticker = ticker.upper()
    
    # Display results
    if 'results' in st.session_state:
        results = st.session_state.results
        ticker = st.session_state.ticker
        
        # Company header
        company_name = results['info'].get('shortName', ticker)
        st.header(f"{company_name} ({ticker}) - DCF Analysis")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Current Price",
                f"${results['price']:.2f}"
            )
        
        with col2:
            create_metric_card(
                "DCF Value Per Share",
                f"${results['value_per_share']:.2f}"
            )
        
        with col3:
            mos = results['margin_of_safety']
            create_metric_card(
                "Margin of Safety",
                f"{mos:.1f}%",
                delta=mos
            )
        
        with col4:
            create_metric_card(
                "Growth Rate",
                f"{results['chosen_growth']:.1%}",
                suffix=f" ({results['growth_source']})"
            )
        
        # Create tabs for different sections
        tabs = st.tabs([
            "📊 Valuation Summary",
            "📜 Historical Data",
            "🔮 Projections",
            "🔍 Sensitivity Analysis",
            "🎯 Fundamental Analysis",
            "📈 Technical Dashboard"             
        ])
        
        # Tab 1: Valuation Summary
        with tabs[0]:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<div class="container-header">Key Valuation Metrics</div>', unsafe_allow_html=True)
                
                # Create two columns within the card
                vcol1, vcol2 = st.columns(2)
                
                with vcol1:
                    st.markdown("**Growth Rates**")
                    st.markdown(f"Historical CAGR: {results['hist_growth']:.1%}")
                    st.markdown(f"Revenue Growth: {results['info'].get('revenueGrowth', 'N/A') if isinstance(results['info'].get('revenueGrowth'), (int, float)) else 'N/A'}")
                    st.markdown(f"Using Growth Rate: {results['chosen_growth']:.1%} ({results['growth_source']})")
                
                with vcol2:
                    st.markdown("**Valuation Details**")
                    st.markdown(f"Enterprise Value: ${results['enterprise_value']/1e6:.1f}M")
                    st.markdown(f"Shares Outstanding: {results['shares']/1e6:.1f}M")
                    st.markdown(f"Discount Rate: {discount_rate:.1%}")
                    st.markdown(f"Terminal Growth: {terminal_growth_rate:.1%}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Company info card
                st.markdown('<div class="container-header">Company Information</div>', unsafe_allow_html=True)
                
                # Create two columns for company info
                ccol1, ccol2 = st.columns(2)
                
                with ccol1:
                    st.markdown("**Market Metrics**")
                    st.markdown(f"P/E Ratio (TTM): {results['info'].get('trailingPE', 'N/A') if isinstance(results['info'].get('trailingPE'), (int, float)) else 'N/A'}")
                    st.markdown(f"Forward P/E: {results['info'].get('forwardPE', 'N/A') if isinstance(results['info'].get('forwardPE'), (int, float)) else 'N/A'}")
                    st.markdown(f"Market Cap: ${results['info'].get('marketCap', 0)/1e9:.1f}B")
                    st.markdown(f"Dividend Yield: {results['info'].get('dividendYield', 0)*100:.2f}%")
                
                with ccol2:
                    st.markdown("**Financial Health**")
                    st.markdown(f"Debt/Equity: {results['info'].get('debtToEquity', 'N/A') if isinstance(results['info'].get('debtToEquity'), (int, float)) else 'N/A'}")
                    st.markdown(f"Return on Equity: {results['info'].get('returnOnEquity', 0)*100:.2f}%")
                    st.markdown(f"Operating Margin: {results['info'].get('operatingMargins', 0)*100:.2f}%")
                    st.markdown(f"Beta: {results['info'].get('beta', 'N/A') if isinstance(results['info'].get('beta'), (int, float)) else 'N/A'}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # DCF Analysis Explanation
                st.markdown('<div class="container-header">Valuation Analysis</div>', unsafe_allow_html=True)
                
                valuation_status = "Undervalued" if results['value_per_share'] > results['price'] else "Overvalued"
                valuation_color = "#4CAF50" if valuation_status == "Undervalued" else "#F44336"
                
                st.markdown(f"""
                <div style="display:flex;align-items:center;margin-bottom:15px;">
                    <div style="width:15px;height:15px;background-color:{valuation_color};border-radius:50%;margin-right:10px;"></div>
                    <div style="font-size:1.5rem;font-weight:600;color:{valuation_color};">{valuation_status}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                The DCF analysis suggests that {ticker} is currently **{valuation_status.lower()}** by 
                {abs(results['margin_of_safety']):.1f}% compared to its intrinsic value.
                
                Current price: **${results['price']:.2f}**  
                DCF fair value: **${results['value_per_share']:.2f}**
                
                **Analysis Parameters:**
                - Discount Rate: {discount_rate:.1%}
                - Growth Rate: {results['chosen_growth']:.1%}
                - Terminal Growth: {terminal_growth_rate:.1%}
                - Projection Years: {projection_years}
                """)
                
                # Show company description if available
                if 'longBusinessSummary' in results['info']:
                    with st.expander("Company Description"):
                        st.markdown(results['info']['longBusinessSummary'])
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 2: Historical Data
        with tabs[1]:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<div class="container-header">Historical Free Cash Flow</div>', unsafe_allow_html=True)
                
                # Display historical FCF data
                hist_df = format_table_for_display(results['historic_fcf_df'])
                hist_df['Free Cash Flow (Millions)'] = hist_df['Free Cash Flow'] / 1e6
                hist_df = hist_df.drop(columns=['Free Cash Flow'])
                st.dataframe(hist_df, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="container-header">Historical FCF Visualization</div>', unsafe_allow_html=True)
                
                # Display historical FCF chart
                st.plotly_chart(results['hist_chart'], use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 3: Projections
        with tabs[2]:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<div class="container-header">Projected Cash Flows</div>', unsafe_allow_html=True)
                
                # Display projected FCF data
                proj_df = format_table_for_display(results['projections_df'])
                proj_df['Projected FCF (Millions)'] = proj_df['Projected FCF'] / 1e6
                proj_df['Discounted FCF (Millions)'] = proj_df['Discounted FCF'] / 1e6
                proj_df = proj_df.drop(columns=['Projected FCF', 'Discounted FCF'])
                st.dataframe(proj_df, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="container-header">Projected FCF Visualization</div>', unsafe_allow_html=True)
                
                # Display projected FCF chart
                st.plotly_chart(results['proj_chart'], use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 4: Sensitivity Analysis
        with tabs[3]:
            st.markdown('<div class="container-header">Sensitivity Analysis</div>', unsafe_allow_html=True)
            
            st.markdown("""
            This analysis shows how the DCF value per share changes with different discount rates (rows) 
            and terminal growth rates (columns).
            
            - **Green** indicates scenarios where the stock is undervalued (higher than current price)
            - **Yellow** indicates scenarios close to current price
            - **Red** indicates scenarios where the stock is overvalued (lower than current price)
            - **Gray** indicates invalid scenarios (where terminal growth ≥ discount rate)
            """)
            
            # Create tabs for different growth rates
            sens_tabs = st.tabs([f"Growth: {k}" for k in results['sensitivity'].keys()])
            
            for i, (k, v) in enumerate(results['sensitivity'].items()):
                with sens_tabs[i]:
                    # Apply styling to the sensitivity table
                    styled_df = style_sensitivity_table(v, results['price'])
                    st.dataframe(styled_df, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        with tabs[4]:
            if 'results' in st.session_state and st.session_state.results:
                display_fundamental_analysis(
                    ticker,
                    st.session_state.results.get('fundamental_metrics'),
                    st.session_state.results.get('piotroski_data'),
                    st.session_state.results.get('scorecard')
                )
        with tabs[5]:  # Technical Dashboard tab

            st.markdown('<div class="container-header">📈 Technical Analysis Dashboard</div>', unsafe_allow_html=True)
            
            # Check if results exist and contain price data
            if 'results' in st.session_state and st.session_state.results.get('price_df') is not None:
                results = st.session_state.results
                price_df = results['price_df']
                
                # Technical Analysis Summary Cards
                col1, col2, col3, col4 = st.columns(4)
                
                if not price_df.empty:
                    latest = price_df.iloc[-1]
                    
                    with col1:
                        # RSI Card
                        if 'RSI14' in price_df.columns:
                            rsi_value = latest['RSI14']
                            if pd.notna(rsi_value):
                                rsi_color = "#FF1744" if rsi_value > 70 else "#4CAF50" if rsi_value < 30 else "#FF9800"
                                rsi_status = "Overbought" if rsi_value > 70 else "Oversold" if rsi_value < 30 else "Neutral"
                                create_technical_metric_card("RSI (14)", f"{float(rsi_value):.1f}", rsi_status, rsi_color)
                            else:
                                create_technical_metric_card("RSI (14)", "N/A", "Calculating...", "#666666")
                        else:
                            create_technical_metric_card("RSI (14)", "N/A", "Not Available", "#666666")
                    
                    with col2:
                        # MACD Card
                        if 'MACD_12_26_9' in price_df.columns and 'MACDs_12_26_9' in price_df.columns:
                            macd_value = latest['MACD_12_26_9']
                            macd_signal = latest['MACDs_12_26_9']
                            if pd.notna(macd_value) and pd.notna(macd_signal):
                                macd_hist = float(macd_value) - float(macd_signal)
                                macd_color = "#4CAF50" if macd_hist > 0 else "#FF1744"
                                macd_status = "Bullish" if macd_hist > 0 else "Bearish"
                                create_technical_metric_card("MACD Histogram", f"{macd_hist:.3f}", macd_status, macd_color)
                            else:
                                create_technical_metric_card("MACD Histogram", "N/A", "Calculating...", "#666666")
                        else:
                            create_technical_metric_card("MACD Histogram", "N/A", "Not Available", "#666666")
                    
                    with col3:
                        # Moving Average Trend Card
                        if 'SMA10' in price_df.columns and 'SMA40' in price_df.columns:
                            SMA10 = latest['SMA10']
                            SMA40 = latest['SMA40']
                            if pd.notna(SMA10) and pd.notna(SMA40):
                                trend_color = "#4CAF50" if SMA10 > SMA40 else "#FF1744"
                                trend_status = "Weekly Golden Cross" if SMA10 > SMA40 else "Weekly Death Cross"
                                create_technical_metric_card("MA Trend", f"{float(SMA10):.2f}", trend_status, trend_color)
                            else:
                                create_technical_metric_card("MA Trend", "N/A", "Calculating...", "#666666")
                        else:
                            create_technical_metric_card("MA Trend", "N/A", "Not Available", "#666666")
                    
                    with col4:
                        # Price vs SMA10 Card
                        if 'SMA10' in price_df.columns:
                            current_price = latest['Close']
                            SMA10 = latest['SMA10']
                            if pd.notna(current_price) and pd.notna(SMA10):
                                price_vs_sma = ((current_price - SMA10) / SMA10) * 100
                                price_color = "#4CAF50" if price_vs_sma > 0 else "#FF1744"
                                price_status = f"{price_vs_sma:.1f}% vs SMA10"
                                create_technical_metric_card("Price Position", f"${float(current_price):.2f}", price_status, price_color)
                            else:
                                create_technical_metric_card("Price Position", "N/A", "Calculating...", "#666666")
                        else:
                            create_technical_metric_card("Price Position", "N/A", "Not Available", "#666666")
                
                # Main Charts Section
                st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
                
                # Create two columns for charts
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    if 'SMA10' in price_df.columns and 'SMA40' in price_df.columns:
                        st.subheader("📊 Weekly Price & Moving Averages")
                        
                        fig_price = go.Figure()
                        
                        # Add price line
                        fig_price.add_trace(go.Scatter(
                            x=price_df.index, 
                            y=price_df["Close"],
                            name="Weekly Close", 
                            line=dict(color="#1E88E5", width=2)
                        ))
        
                        # Add weekly SMAs
                        fig_price.add_trace(go.Scatter(
                            x=price_df.index, 
                            y=price_df["SMA10"],
                            name="SMA 10-Week (~2.5 months)", 
                            line=dict(color="#FF9800", width=2)
                        ))
                        
                        fig_price.add_trace(go.Scatter(
                            x=price_df.index, 
                            y=price_df["SMA40"],
                            name="SMA 40-Week (~10 months)", 
                            line=dict(color="#FF1744", width=2)
                        ))
                        
                        # Update layout with your existing dark theme
                        fig_price.update_layout(
                            template="plotly_dark",
                            plot_bgcolor="#181c24",
                            paper_bgcolor="#232936",
                            font=dict(color="#e0e6ed"),
                            margin=dict(l=40, r=40, t=40, b=40),
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=True, gridcolor="#394867"),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_price, use_container_width=True)
                    else:
                        st.info("📊 Moving averages data not available")
                
                with chart_col2:
                    # RSI Chart
                    if 'RSI14' in price_df.columns and price_df['RSI14'].notna().any():
                        st.subheader("🎯 RSI (14) Indicator")
                        
                        fig_rsi = go.Figure()
                        
                        # Add RSI line
                        fig_rsi.add_trace(go.Scatter(
                            x=price_df.index,
                            y=price_df['RSI14'],
                            name="RSI",
                            line=dict(color="#9C27B0", width=2),
                            hovertemplate="<b>RSI</b>: %{y:.1f}<br><b>Date</b>: %{x}<extra></extra>"
                        ))
                        
                        # Add overbought/oversold lines
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#FF1744", 
                                        annotation_text="Overbought (70)", annotation_position="bottom right")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#4CAF50", 
                                        annotation_text="Oversold (30)", annotation_position="top right")
                        
                        # Fill areas
                        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="#FF1744", opacity=0.1, line_width=0)
                        fig_rsi.add_hrect(y0=0, y1=30, fillcolor="#4CAF50", opacity=0.1, line_width=0)
                        
                        fig_rsi.update_layout(
                            template="plotly_dark",
                            plot_bgcolor="#181c24",
                            paper_bgcolor="#232936",
                            font=dict(color="#e0e6ed"),
                            margin=dict(l=40, r=40, t=40, b=40),
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=True, gridcolor="#394867", range=[0, 100]),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_rsi, use_container_width=True)
                    else:
                        st.info("🎯 RSI indicator data not available")
                
                # MACD Chart (full width)
                if 'MACD_12_26_9' in price_df.columns and 'MACDs_12_26_9' in price_df.columns:
                    st.subheader("⚡ MACD Indicator")
                    
                    fig_macd = go.Figure()
                    
                    # Add MACD line
                    fig_macd.add_trace(go.Scatter(
                        x=price_df.index,
                        y=price_df['MACD_12_26_9'],
                        name="MACD",
                        line=dict(color="#00BCD4", width=2),
                        hovertemplate="<b>MACD</b>: %{y:.3f}<br><b>Date</b>: %{x}<extra></extra>"
                    ))
                    
                    # Add Signal line
                    fig_macd.add_trace(go.Scatter(
                        x=price_df.index,
                        y=price_df['MACDs_12_26_9'],
                        name="Signal",
                        line=dict(color="#FF5722", width=2),
                        hovertemplate="<b>Signal</b>: %{y:.3f}<br><b>Date</b>: %{x}<extra></extra>"
                    ))
                    
                    # Add histogram
                    histogram = price_df['MACD_12_26_9'] - price_df['MACDs_12_26_9']
                    colors = ['#4CAF50' if x >= 0 else '#FF1744' for x in histogram]
                    
                    fig_macd.add_trace(go.Bar(
                        x=price_df.index,
                        y=histogram,
                        name="Histogram",
                        marker_color=colors,
                        opacity=0.6,
                        hovertemplate="<b>Histogram</b>: %{y:.3f}<br><b>Date</b>: %{x}<extra></extra>"
                    ))
                    
                    # Add zero line
                    fig_macd.add_hline(y=0, line_dash="dash", line_color="#666666", line_width=1)
                    
                    fig_macd.update_layout(
                        template="plotly_dark",
                        plot_bgcolor="#181c24",
                        paper_bgcolor="#232936",
                        font=dict(color="#e0e6ed"),
                        margin=dict(l=40, r=40, t=40, b=40),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#394867"),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_macd, use_container_width=True)
                else:
                    st.info("⚡ MACD indicator data not available")
                
                # Market Breadth Section
                if results.get('breadth_data') is not None:
                    st.subheader("📈 Market Breadth (NYSE A/D Line)")
                    breadth_data = results['breadth_data']
                    
                    fig_breadth = go.Figure()
                    fig_breadth.add_trace(go.Scatter(
                        x=breadth_data.index, 
                        y=breadth_data['ADLine'],
                        name="Advance/Decline Line", 
                        line=dict(color="#4CAF50", width=2),
                        fill='tonexty',
                        fillcolor='rgba(76, 175, 80, 0.1)',
                        hovertemplate="<b>A/D Line</b>: %{y:.0f}<br><b>Date</b>: %{x}<extra></extra>"
                    ))
                    
                    fig_breadth.update_layout(
                        template="plotly_dark",
                        plot_bgcolor="#181c24",
                        paper_bgcolor="#232936",
                        font=dict(color="#e0e6ed"),
                        margin=dict(l=40, r=40, t=40, b=40),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#394867"),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_breadth, use_container_width=True)
                else:
                    st.info("📈 Market breadth data currently unavailable")
                
                # Trading Signals Summary
                st.markdown('<div class="container-header">🎯 Trading Signals Summary</div>', unsafe_allow_html=True)
                
                # Create signals summary
                signals_summary = []
                
                if 'RSI14' in price_df.columns and pd.notna(latest.get('RSI14')):
                    rsi_val = latest['RSI14']
                    if rsi_val > 70:
                        signals_summary.append("🔴 **RSI Overbought** - Consider taking profits")
                    elif rsi_val < 30:
                        signals_summary.append("🟢 **RSI Oversold** - Potential buying opportunity")
                    else:
                        signals_summary.append("🟡 **RSI Neutral** - No clear signal")
                
                if 'MACD_12_26_9' in price_df.columns and 'MACDs_12_26_9' in price_df.columns:
                    if pd.notna(latest.get('MACD_12_26_9')) and pd.notna(latest.get('MACDs_12_26_9')):
                        macd_hist = latest['MACD_12_26_9'] - latest['MACDs_12_26_9']
                        if macd_hist > 0:
                            signals_summary.append("🟢 **MACD Bullish** - Momentum is positive")
                        else:
                            signals_summary.append("🔴 **MACD Bearish** - Momentum is negative")
                
                if 'SMA10' in price_df.columns and 'SMA40' in price_df.columns:
                    if pd.notna(latest.get('SMA10')) and pd.notna(latest.get('SMA40')):
                        if latest['SMA10'] > latest['SMA40']:
                            signals_summary.append("🟢 **Weekly Golden Cross** - Long-term uptrend intact")
                        else:
                            signals_summary.append("🔴 **Weekly Death Cross** - Long-term downtrend")
                
                if signals_summary:
                    for signal in signals_summary:
                        st.markdown(signal)
                else:
                    st.info("🎯 Unable to generate trading signals - insufficient data")
                
                # Disclaimer
                st.markdown("""
                ---
                **⚠️ Disclaimer:** This technical analysis is for educational purposes only and should not be considered as financial advice. 
                Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
                """)
            
            else:
                st.warning("⚠️ Technical analysis data not available. Please calculate DCF analysis first by clicking the 'Calculate DCF Value' button.")


                                
    # Footer
    st.markdown("""---""")
    st.markdown(
        """<div style="text-align:center;color:#666;font-size:0.8rem;">
        DCF Valuation Tool © 2025 | Data provided by Yahoo Finance
        </div>""",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    app()

    # Run the Streamlit app
    # streamlit run app.py