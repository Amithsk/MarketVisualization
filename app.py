# app.py
import streamlit as st
import pandas as pd
from queries import (
    get_nifty_recent, get_predictions, get_model_daily_summary,
    get_comparisons, get_intraday_for_symbol, get_gainers_losers,
    get_etf_list, get_etf_price_history
)
from components import plot_candles, line_series, simple_bar

st.set_page_config(layout="wide", page_title="MCP - Market Control Panel")

st.title("Master Control Panel — Market Visualizations")

tabs = st.tabs(["Market Overview", "Intraday Panel", "ETF Tracker", "Prediction & Model Health"])

# MARKET OVERVIEW
with tabs[0]:
    st.header("Market Overview — NIFTY")
    ndays = st.slider("Days to display", min_value=30, max_value=720, value=180)
    nifty_df = get_nifty_recent(days=ndays)
    st.subheader("NIFTY Price Chart (OHLC)")
    fig = plot_candles(nifty_df, date_col='Date', title=f"NIFTY Last {ndays} days")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("NIFTY Indicators")
    col1, col2, col3 = st.columns(3)
    last = nifty_df.iloc[-1]
    col1.metric("Close", f"{last['Close']:.2f}", delta=f"{last['Close']-nifty_df['Close'].iloc[-2]:.2f}")
    col2.metric("SMA20", f"{last['SMA_20']:.2f}" if pd.notna(last['SMA_20']) else "n/a")
    col3.metric("RSI", f"{last['RSI']:.2f}" if pd.notna(last['RSI']) else "n/a")

    st.markdown("**Gainers / Losers (recent)**")
    gl = get_gainers_losers(top_n=10)
    st.dataframe(gl)

# INTRADAY PANEL
with tabs[1]:
    st.header("Intraday Performance Panel")
    symbol = st.text_input("Symbol (exact)", value="RELIANCE.NS")
    days_intraday = st.slider("Days", 1, 365, 30)
    if symbol:
        intr = get_intraday_for_symbol(symbol, days=days_intraday)
        if intr.empty:
            st.warning("No data for that symbol in intraday_bhavcopy. Confirm symbol.")
        else:
            st.plotly_chart(plot_candles(intr.rename(columns={"trade_date":"Date"})), use_container_width=True)
            st.write("Recent table")
            st.dataframe(intr.tail(50))

# ETF TRACKER
with tabs[2]:
    st.header("ETF Tracker")
    etf_list = get_etf_list()
    etf_choice = st.selectbox("ETF", etf_list['etf_symbol'] + " — " + etf_list['etf_name'].fillna(''))
    etf_id = etf_list[etf_list['etf_symbol'] == etf_choice.split(" — ")[0]]['etf_id'].iloc[0]
    etf_history = get_etf_price_history(etf_id, days=365)
    if not etf_history.empty:
        st.plotly_chart(plot_candles(etf_history.rename(columns={"trade_date":"Date","close":"Close"})), use_container_width=True)
        st.dataframe(etf_history.tail(50))
    else:
        st.info("No transaction history found for this ETF.")

# PREDICTION & MODEL HEALTH
with tabs[3]:
    st.header("Predictions & Model Health")
    models = get_model_daily_summary()
    model_names = models['model_name'].unique().tolist()
    chosen = st.selectbox("Model", options=["ALL"] + model_names)
    days = st.slider("Model history days", 7, 365, 90)
    if chosen == "ALL":
        summary = get_model_daily_summary(last_days=days)
    else:
        summary = get_model_daily_summary(model_name=chosen, last_days=days)
    st.subheader("Daily Summary")
    st.dataframe(summary)

    st.subheader("Forward Predictions (recent)")
    preds = get_predictions(model_name=None if chosen=="ALL" else chosen, only_forward=True, limit=200)
    st.dataframe(preds)

    st.subheader("Backtest Comparison (recent)")
    comp = get_comparisons(model_name=None if chosen=="ALL" else chosen, limit=200)
    st.dataframe(comp)
