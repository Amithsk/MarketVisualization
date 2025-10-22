# app.py
import streamlit as st
import pandas as pd
from queries import (
    get_nifty_recent, get_predictions, get_model_daily_summary,
    get_comparisons, get_intraday_for_symbol,
    get_intraday_by_date, get_gainers_losers,get_intraday_market_rows,get_intraday_top_value_traded, 
    get_intraday_top_price_movers,get_intraday_summary_kpis,
    get_etf_list, get_etf_price_history,get_etf_by_date
)

from components import plot_candles, line_series, simple_bar, bar_with_labels

st.set_page_config(layout="wide", page_title="Market Visualizations")

st.title("Market Visualizations")

tabs = st.tabs(["Market Overview", "Intraday Panel", "ETF Tracker", "Prediction & Model Health"])

# --- Helper: colorize table rows ---
def colorize_intraday_table(df: pd.DataFrame):
    if df is None or df.empty:
        return df
    def _row_color(row):
        if "direction" in row:
            if row["direction"] == "gain":
                return ["background-color: #e6ffe6"] * len(row)
            elif row["direction"] == "loss":
                return ["background-color: #ffe6e6"] * len(row)
            else:
                return ["background-color: #f2f2f2"] * len(row)
        elif "pct_change" in row:
            if row["pct_change"] > 2:
                return ["background-color: #d9fcd9"] * len(row)
            elif row["pct_change"] < -2:
                return ["background-color: #fcd9d9"] * len(row)
            else:
                return ["background-color: #f2f2f2"] * len(row)
        return [""] * len(row)
    return df.style.apply(_row_color, axis=1)


# MARKET OVERVIEW
with tabs[0]:
    st.header("Market Overview — NIFTY")
    ndays = st.slider("Days to display", min_value=30, max_value=720, value=180)
    nifty_df = get_nifty_recent(days=ndays)
    st.subheader("NIFTY Price Chart (OHLC)")
    fig = plot_candles(nifty_df, date_col='Date', title=f"NIFTY Last {ndays} days")
    st.plotly_chart(fig, width='stretch')

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
# ------------------- INTRADAY PANEL (replace existing block) -------------------
with tabs[1]:
    st.header("Intraday Performance Panel")

    mode = st.radio("View Mode", ["By Symbol", "By Date"], horizontal=True)

    # default trade_date string used for functions that accept a date
    trade_date_str = None

    if mode == "By Symbol":
        # By symbol mode remains unchanged — shows symbol history
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

        # keep trade_date_str as None so subsequent calls fall back to today's data
        trade_date_str = None

    else:  # By Date
        from datetime import date, timedelta
        sel_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1),key="intraday_date_input")
        trade_date_str = sel_date.strftime("%Y-%m-%d")

        # use existing helper that fetches all rows for that date
        df = get_intraday_by_date(trade_date_str)

        if df.empty:
            st.info(f"No data found in intraday_bhavcopy for {trade_date_str}.")
        else:
            st.subheader(f"Market Summary — {trade_date_str}")
            st.metric("Stocks traded", len(df))
            # Use the fetched df for the snapshot display to avoid duplicate DB calls
            st.dataframe(df.head(100))

            st.subheader("Top 10 by Value Traded")
            top = df.nlargest(10, "net_trdval")[["symbol", "open", "close", "net_trdval"]]
            st.bar_chart(top.set_index("symbol")["net_trdval"])

            st.subheader("Top 10 Price Movers (%)")
            df["pct_change"] = ((df["close"] - df["open"]) / df["open"]) * 100
            movers = df.nlargest(10, "pct_change")[["symbol", "pct_change"]]
            st.bar_chart(movers.set_index("symbol"))

        # --- KPIs (now use selected trade_date if in By Date, else today) ---
        kpi_data = get_intraday_summary_kpis(trade_date=trade_date_str)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Symbols Traded", kpi_data["symbols_traded"])
        col2.metric("Total Traded Value", f"{kpi_data['total_traded_value']:,.0f}")
        col3.metric("Gainers", kpi_data["gainers"])
        col4.metric("Losers", kpi_data["losers"])
        col5.metric("Avg % Change", f"{kpi_data['avg_pct_change']}%")

        st.divider()

        # --- Market snapshot ---
        st.subheader("Market Snapshot")
        # If the By Date branch already fetched all rows (df), reuse it; otherwise call query
        if mode == "By Date":
            intraday_df = df  # df was set above
        else:
            intraday_df = get_intraday_market_rows(trade_date=trade_date_str)

        if intraday_df is not None and not intraday_df.empty:
            st.dataframe(
                colorize_intraday_table(intraday_df),
             use_container_width=True,
             hide_index=True,
              )
        else:
            st.info("No intraday data available for the selected date.")

        st.divider()

        # --- Top 10 by traded value ---
        st.subheader("Top 10 Stocks by Traded Value (with 30-Day Average)")
     
        top_value_df = get_intraday_top_value_traded(trade_date=trade_date_str)
        print("DEBUG trade_date type:", type(trade_date_str), "value:", trade_date_str)
        if top_value_df is not None and not top_value_df.empty:
            st.dataframe(
            colorize_intraday_table(top_value_df),
            use_container_width=True,
            hide_index=True,
            )
        else:
            st.info("No traded value data available for the selected date.")

        st.divider()

        # --- Top gainers and losers ---
        st.subheader("Top 10 Price Movers")
        gainers_df, losers_df = get_intraday_top_price_movers(trade_date=trade_date_str)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top Gainers**")
            if gainers_df is not None and not gainers_df.empty:
                st.dataframe(
                colorize_intraday_table(gainers_df),
                use_container_width=True,
                hide_index=True,
                )
            else:
                st.info("No gainers data for the selected date.")

        with col2:
            st.markdown("**Top Losers**")
            if losers_df is not None and not losers_df.empty:
                st.dataframe(
                colorize_intraday_table(losers_df),
                use_container_width=True,
                hide_index=True,
             )
            else:
                st.info("No losers data for the selected date.")
# ---------------------------------------------------------------------------


# ETF TRACKER
with tabs[2]:
    st.header("ETF Tracker")

    view_mode = st.radio("View Mode", ["By ETF", "By Date"], horizontal=True)

    if view_mode == "By ETF":
        # existing behavior (single ETF selection)
        etf_list = get_etf_list()
        if etf_list.empty:
            st.info("No ETFs available in etf table.")
        else:
            etf_choices = (etf_list['etf_symbol'] + " — " + etf_list['etf_name'].fillna("")).tolist()
            etf_choice = st.selectbox("ETF", options=etf_choices)
            sel_symbol = etf_choice.split(" — ")[0]
            etf_id = int(etf_list[etf_list['etf_symbol'] == sel_symbol]['etf_id'].iloc[0])
            etf_history = get_etf_price_history(etf_id, days=365)
            if not etf_history.empty:
                # ensure proper column names (get_etf_price_history should canonicalize)
                st.plotly_chart(plot_candles(etf_history), use_container_width=True)
                st.dataframe(etf_history.tail(50))
            else:
                st.info("No transaction history found for this ETF.")

    else:
        # By Date view: show market summary for ETFs on a chosen date
        from datetime import date, timedelta
        sel_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1),key="etf_date_input")
        date_str = sel_date.strftime("%Y-%m-%d")

        df = get_etf_by_date(date_str)
        if df is None or df.empty:
            st.info(f"No ETF transactions found for {date_str}.")
        else:
            st.subheader(f"ETF Market Summary — {date_str}")
            st.metric("ETFs traded", len(df))

            # prefer TradedValue, otherwise use Volume
            ycol = "TradedValue" if "TradedValue" in df.columns and df["TradedValue"].notna().any() else "Volume"

            st.plotly_chart(bar_with_labels(df, x_col="etf_symbol", y_col=ycol, title=f"Top ETFs by {ycol} on {date_str}", text_format=".0f", max_items=40), use_container_width=True)

            # show table
            st.dataframe(df.head(200))

            # drill-down: choose an ETF from today's list
            st.subheader("Drill-down ETF")
            choices = df["etf_symbol"].dropna().unique().tolist()
            sel = st.selectbox("Pick ETF for history", options=["-- none --"] + choices)
            if sel and sel != "-- none --":
                etf_id = int(df[df["etf_symbol"] == sel]["etf_id"].iloc[0])
                etf_history = get_etf_price_history(etf_id, days=365)
                if etf_history is None or etf_history.empty:
                    st.warning("No historical data available for selected ETF.")
                else:
                    etf_history["Date"] = pd.to_datetime(etf_history["Date"])
                    st.plotly_chart(plot_candles(etf_history, title=f"{sel} — 1y history"), use_container_width=True)
                    # show recent numbers inside chart table — present tail
                    st.dataframe(etf_history.tail(50))


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


