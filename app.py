# app.py
import streamlit as st
import pandas as pd
from queries import (
    get_nifty_recent, get_predictions, get_model_daily_summary,
    get_comparisons, get_intraday_for_symbol, get_gainers_losers,
    get_etf_list, get_etf_price_history,get_intraday_by_date
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
# app.py  – inside Intraday tab
with tabs[1]:
    st.header("Intraday Performance Panel")

    mode = st.radio("View Mode", ["By Symbol", "By Date"], horizontal=True)

    if mode == "By Symbol":
        symbol = st.text_input("Symbol (exact)", value="RELIANCE.NS")
        days_intraday = st.slider("Days", 1, 365, 30)
        if symbol:
            intr = get_intraday_for_symbol(symbol, days=days_intraday)
            if intr.empty:
                st.warning("No data for that symbol in intraday_bhavcopy. Confirm symbol.")
            else:
                intr = intr.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                                            "low": "Low", "close": "Close"})
                st.plotly_chart(plot_candles(intr), use_container_width=True)
                st.dataframe(intr.tail(50))

    else:  # By Date
        from datetime import date, timedelta
        sel_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1))
        df = get_intraday_by_date(sel_date.strftime("%Y-%m-%d"))

        if df.empty:
            st.info(f"No data found in intraday_bhavcopy for {sel_date}.")
        else:
            st.subheader(f"Market Summary — {sel_date}")
            st.metric("Stocks traded", len(df))
            st.dataframe(df.head(100))

            st.subheader("Top 10 by Value Traded")
            top = df.nlargest(10, "net_trdval")[["symbol", "open", "close", "net_trdval"]]
            st.bar_chart(top.set_index("symbol")["net_trdval"])

            st.subheader("Top 10 Price Movers (%)")
            df["pct_change"] = ((df["close"] - df["open"]) / df["open"]) * 100
            movers = df.nlargest(10, "pct_change")[["symbol", "pct_change"]]
            st.bar_chart(movers.set_index("symbol"))


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
