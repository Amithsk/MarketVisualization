# app.py
import streamlit as st
import datetime
from datetime import date, timedelta
import pandas as pd
from io import StringIO
import json

from queries import (
    get_nifty_recent, get_predictions, get_model_daily_summary,
    get_comparisons, get_intraday_for_symbol,
    get_intraday_by_date, get_gainers_losers, get_intraday_market_rows, get_intraday_top_value_traded,
    get_intraday_top_price_movers, get_intraday_summary_kpis, get_signal_summary_by_day_strategy,
    get_signals_by_date_strategy, get_feature_trends, get_strategy_runs,
    get_latest_prior_trading_date, get_smart_symbols,
    get_signals_for_date, get_strategy_features,
    get_etf_list, get_etf_price_history, get_etf_by_date
)

from components import plot_candles, line_series, simple_bar, bar_with_labels, pie_split
pd.options.display.float_format = "{:.2f}".format
st.set_page_config(layout="wide", page_title="Market Visualizations")

st.title("Market Visualizations")

tabs = st.tabs(["Market Overview", "Intraday Panel", "ETF Tracker", "Prediction & Model Health"])


# --- Helper: colorize table rows ---
def colorize_intraday_table(df: pd.DataFrame, decimals: int = 2):
    """
    Return a pandas Styler that colors rows and formats numeric columns to `decimals` places.
    Safe: handles non-numeric columns.
    """
    if df is None or df.empty:
        return df

    # work on a copy and round numeric columns
    dfr = df.copy()
    num_cols = dfr.select_dtypes(include="number").columns.tolist()
    if num_cols:
        dfr[num_cols] = dfr[num_cols].round(decimals)

    def _row_color(row):
        # row is a Series of values (already rounded for numeric)
        if "direction" in row.index:
            if row["direction"] == "gain":
                return ["background-color: #e6ffe6"] * len(row)
            elif row["direction"] == "loss":
                return ["background-color: #ffe6e6"] * len(row)
            else:
                return ["background-color: #f2f2f2"] * len(row)
        elif "pct_change" in row.index:
            # use rounded value for thresholds
            try:
                val = float(row["pct_change"])
            except Exception:
                val = 0.0
            if val > 2:
                return ["background-color: #d9fcd9"] * len(row)
            elif val < -2:
                return ["background-color: #fcd9d9"] * len(row)
            else:
                return ["background-color: #f2f2f2"] * len(row)
        return [""] * len(row)

    styler = dfr.style.apply(_row_color, axis=1)

    # Format numeric cols explicitly to ensure .2f-like display in the styler
    if num_cols:
        fmt = {c: f"{{:.{decimals}f}}" for c in num_cols}
        styler = styler.format(fmt)

    return styler


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
    st.dataframe(gl.round(2))


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
            if intr is None or intr.empty:
                st.warning("No data for that symbol in intraday_bhavcopy. Confirm symbol.")
            else:
                intr = intr.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                                            "low": "Low", "close": "Close"})
                st.plotly_chart(plot_candles(intr), use_container_width=True)
                st.dataframe(intr.tail(50).round(2))

        # keep trade_date_str as None so subsequent calls fall back to today's data
        trade_date_str = None

    else:  # By Date
        sel_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1), key="intraday_date_input")
        trade_date_str = sel_date.strftime("%Y-%m-%d")

        # use existing helper that fetches all rows for that date
        df = get_intraday_by_date(trade_date_str)

        if df is None or df.empty:
            st.info(f"No data found in intraday_bhavcopy for {trade_date_str}.")
        else:
            st.subheader(f"Market Summary — {trade_date_str}")
            st.metric("Stocks traded", len(df))
            # Use the fetched df for the snapshot display to avoid duplicate DB calls
            st.dataframe(df.head(100).round(2))

            st.subheader("Top 10 by Value Traded")
            top = df.nlargest(10, "net_trdval")[["symbol", "open", "close", "net_trdval"]]
            st.plotly_chart(
                bar_with_labels(
                    top,
                    x_col="symbol",
                    y_col="net_trdval",
                    title="Top 10 Stocks by Value Traded",
                    text_format=".0f",
                    max_items=10,
                ),
                use_container_width=True,
            )

            st.subheader("Top 10 Price Movers (%)")
            df["pct_change"] = ((df["close"] - df["open"]) / df["open"]) * 100
            movers = df.nlargest(10, "pct_change")[["symbol", "pct_change"]]
            st.plotly_chart(
                bar_with_labels(
                    movers,
                    x_col="symbol",
                    y_col="pct_change",
                    title="Top 10 Price Movers (%)",
                    text_format=".2f",
                    max_items=10,
                ),
                use_container_width=True,
            )

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

    # -------------------- Signals & Feature Trends Intraday trading --------------------
    st.markdown("## Signals & Strategy Analysis")

    with st.expander("Signals & Strategy — Summary and Explorer", expanded=True):
        col_a, col_b = st.columns([2, 1])

        # Summary Filters
        days = col_b.number_input("Summary lookback (days)", min_value=1, max_value=365, value=30)
        selected_date = col_b.date_input("Signal date", value=date.today() - timedelta(days=1), key="signals_date_input")
        chosen_strategy = col_b.selectbox("Strategy (optional)", options=["-- ALL --"], index=0)

        # Load summary
        summary_df = get_signal_summary_by_day_strategy(last_days=days)
        if summary_df is None or summary_df.empty:
            st.info("No strategy signals found for the chosen period.")
            strategies = ["-- ALL --"]
        else:
            # Update strategy choices if default
            strategies = ["-- ALL --"] + sorted(summary_df["strategy"].dropna().unique().tolist())

        # Let user pick strategy (replace placeholder selectbox if it was placeholder)
        if chosen_strategy == "-- ALL --":
            chosen_strategy = col_b.selectbox("Strategy (optional)", options=strategies, index=0)

        # Aggregate counts by strategy for the period (for bar)
        if summary_df is not None and not summary_df.empty:
            agg = summary_df.groupby("strategy").agg({"c": "sum", "longs": "sum", "shorts": "sum"}).reset_index().sort_values("c", ascending=False)
            st.subheader("Signals by Strategy (last {} days)".format(days))
            st.plotly_chart(bar_with_labels(agg, x_col="strategy", y_col="c", title=f"Signals by strategy — last {days}d"), use_container_width=True)

            # Pie LONG vs SHORT overall
            total_longs = int(agg["longs"].sum())
            total_shorts = int(agg["shorts"].sum())
            st.subheader("LONG vs SHORT (period total)")
            st.plotly_chart(pie_split(["LONG", "SHORT"], [total_longs, total_shorts], title="LONG vs SHORT"), use_container_width=True)

        # Signal Explorer: list of signals for the selected date / strategy
        st.markdown("---")
        st.subheader(f"Signal Explorer — {selected_date.isoformat()}")
        strat_param = None if (chosen_strategy is None or chosen_strategy == "-- ALL --") else chosen_strategy

        # Use existing function for signals fetch
        signals_df = get_signals_by_date_strategy(selected_date.isoformat(), strategy=strat_param, limit=2000)
        if signals_df is None or signals_df.empty:
            # If no signals, show helpful suggestions and last available date button
            st.info(f"No signals for {selected_date.isoformat()}.")
            latest_prior = get_latest_prior_trading_date(selected_date.isoformat())
            if latest_prior:
                if st.button(f"Use latest data: {latest_prior}"):
                    signals_df = get_signals_by_date_strategy(latest_prior, strategy=strat_param, limit=2000)
            # offer recent prior trading dates (prev 5)
            prev_options = []
            cur = pd.to_datetime(selected_date)
            for i in range(1, 8):
                cand = (cur - pd.Timedelta(days=i)).date().isoformat()
                lp = get_latest_prior_trading_date(cand)
                if lp and lp not in prev_options:
                    prev_options.append(lp)
                if len(prev_options) >= 5:
                    break
            if prev_options:
                chosen = st.selectbox("Or choose from prior trading dates", options=["-- none --"] + prev_options, key="prior_dates_sel")
                if chosen and chosen != "-- none --":
                    signals_df = get_signals_by_date_strategy(chosen, strategy=strat_param, limit=2000)

        if signals_df is not None and not signals_df.empty:
            # show the important columns; show params/notes truncated
            show_cols = ["trade_date", "strategy", "symbol", "signal_type", "signal_score", "entry_price", "stop_price", "target_price", "expected_hold_days", "params", "notes"]
            df_show = signals_df[show_cols].copy()
            st.dataframe(df_show, use_container_width=True)

            # Filters on explorer
            st.markdown("**Explorer Filters**")
            col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
            sel_strats = col_f1.multiselect("Strategy (filter)", options=sorted(signals_df["strategy"].dropna().unique().tolist()))
            sel_types = col_f2.multiselect("Signal Type", options=sorted(signals_df["signal_type"].dropna().unique().tolist()))
            min_score = col_f3.slider("Min Score", float(signals_df["signal_score"].min()), float(signals_df["signal_score"].max()), float(signals_df["signal_score"].min()))
            symbol_search = st.text_input("Symbol search (contains)", value="", key="sig_symbol_search")

            # Apply filters client-side for convenience
            filt = signals_df.copy()
            if sel_strats:
                filt = filt[filt["strategy"].isin(sel_strats)]
            if sel_types:
                filt = filt[filt["signal_type"].isin(sel_types)]
            if min_score:
                filt = filt[filt["signal_score"] >= min_score]
            if symbol_search:
                filt = filt[filt["symbol"].str.contains(symbol_search, case=False, na=False)]

            if filt.empty:
                st.info("No signals match the selected filters.")
            else:
                st.write(f"Showing {len(filt)} signals (filtered)")
                st.dataframe(filt.sort_values(by="signal_score", ascending=False).reset_index(drop=True), use_container_width=True)

                # CSV Export
                csv_buf = StringIO()
                export_cols = ["trade_date", "strategy", "symbol", "signal_type", "signal_score", "entry_price", "stop_price", "target_price", "expected_hold_days", "notes"]
                filt[export_cols].to_csv(csv_buf, index=False)
                st.download_button("Download CSV", csv_buf.getvalue(), file_name=f"signals_{selected_date.strftime('%Y%m%d')}.csv", mime="text/csv")

                # Chart selection: choose row index to plot
                chosen_idx = st.number_input("Select table row index to view chart (0..N-1)", min_value=0, max_value=len(filt)-1, value=0, key="sig_row_idx")
                sel_row = filt.reset_index(drop=True).iloc[int(chosen_idx)]
                symbol = sel_row["symbol"]
                intr = get_intraday_for_symbol(symbol, days=90)
                if intr is None or intr.empty:
                    st.warning("No intraday history for selected symbol.")
                else:
                    intr = intr.rename(columns={"trade_date": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close"})
                    overlays = []
                    if pd.notna(sel_row.get("entry_price")):
                        overlays.append({"label": "entry", "price": float(sel_row["entry_price"]), "dash": "dot", "width": 2, "color": "green"})
                    if pd.notna(sel_row.get("stop_price")):
                        overlays.append({"label": "stop", "price": float(sel_row["stop_price"]), "dash": "dash", "width": 2, "color": "red"})
                    if pd.notna(sel_row.get("target_price")):
                        overlays.append({"label": "target", "price": float(sel_row["target_price"]), "dash": "dashdot", "width": 2, "color": "blue"})
                    fig = plot_candles(intr, overlays=overlays, title=f"{symbol} — 90d with signal overlays")
                    st.plotly_chart(fig, use_container_width=True)

        # end signals_df block

    # Feature Trends: Smart / Manual selector
    st.markdown("---")
    st.subheader("Feature Trends (per-symbol)")

    ft_col1, ft_col2 = st.columns([2, 1])
    mode_ft = ft_col2.radio("Mode", ["Smart", "Manual"], index=0, horizontal=False)
    # date range for features
    from_date = ft_col1.date_input("Start date", value=date.today() - timedelta(days=180), key="ft_start")
    to_date = ft_col1.date_input("End date", value=selected_date if 'selected_date' in locals() else date.today() - timedelta(days=1), key="ft_end")
    start_str = from_date.strftime("%Y-%m-%d")
    end_str = to_date.strftime("%Y-%m-%d")

    chosen_symbol = None
    if mode_ft == "Smart":
        # Use smart symbol suggestions based on end date
        candidates = get_smart_symbols(end_str, lookback_days=5, top_k=20)
        if candidates is None or candidates.empty:
            st.info("No smart symbol suggestions found for this date. Try manual mode or change date range.")
        else:
            st.write("Top smart suggestions (pick one):")
            chosen_symbol = st.selectbox("Pick from suggestions", options=candidates["symbol"].tolist(), key="smart_sym_sel")
    else:
        # Manual mode: source symbols from signals first, then intraday table as fallback
        manual_search = st.text_input("Type to filter symbols (contains)", value="", key="manual_sym_search")
        symbol_source = []
        # prefer signals_df if available
        try:
            if 'signals_df' in locals() and signals_df is not None and not signals_df.empty:
                symbol_source = sorted(signals_df["symbol"].dropna().unique().tolist())
        except Exception:
            symbol_source = []
        if not symbol_source:
            intr_today = get_intraday_by_date(end_str)
            if intr_today is not None and not intr_today.empty:
                symbol_source = sorted(intr_today["symbol"].dropna().unique().tolist())
        if manual_search:
            symbol_source = [s for s in symbol_source if manual_search.upper() in s.upper()]
        if symbol_source:
            chosen_symbol = st.selectbox("Choose symbol (manual)", options=["-- none --"] + symbol_source, key="manual_sym_sel")
            if chosen_symbol == "-- none --":
                chosen_symbol = None
        else:
            st.info("No symbols found for manual selection in the selected date range.")

    # Features input
    feat_entry = st.text_input("Features (comma-separated). Example: rsi_14,atr_14,mom_20", value="rsi_14,atr_14,mom_20", key="features_entry")
    features = [f.strip() for f in feat_entry.split(",") if f.strip()]

    if chosen_symbol:
        # fetch features via get_strategy_features if available; otherwise fallback to get_feature_trends
        try:
            feat_ts = get_strategy_features(chosen_symbol, start_date=start_str, end_date=end_str, features=features)
        except TypeError:
            # if function signature differs, try legacy get_feature_trends(symbol, features, start, end)
            try:
                feat_ts = get_feature_trends(chosen_symbol, features, start_date=start_str, end_date=end_str)
            except Exception:
                feat_ts = pd.DataFrame()

        if feat_ts is None or feat_ts.empty:
            st.warning("No feature data found for symbol / features in the selected range.")
        else:
            st.write(f"Showing features for {chosen_symbol} between {start_str} and {end_str}")
            # ensure datetime index if pivoted
            if isinstance(feat_ts.index, pd.DatetimeIndex):
                x_index = feat_ts.index
            elif "trade_date" in feat_ts.columns:
                x_index = pd.to_datetime(feat_ts["trade_date"])
            else:
                x_index = pd.to_datetime(feat_ts.index)

            import plotly.graph_objs as go
            fig = go.Figure()
            for col in feat_ts.columns:
                fig.add_trace(go.Scatter(x=x_index, y=feat_ts[col], mode='lines', name=col))
            fig.update_layout(title=f"{chosen_symbol} — features", height=450, xaxis_title="date")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(feat_ts.tail(50).round(4))
    else:
        st.info("No symbol selected for Feature Trends. Use Smart or Manual mode to select one.")

    # Recent Run Logs
    st.markdown("---")
    st.subheader("Recent Strategy Runs")
    runs = get_strategy_runs(limit=50)
    if runs is None or runs.empty:
        st.info("No strategy_runs entries found.")
    else:
        # show run_name, started_at, finished_at and parsed summary
        runs_display = runs[["run_name", "started_at", "finished_at", "summary"]].copy()
        runs_display["summary_short"] = runs_display["summary"].apply(lambda s: (s if s is None else (s if len(str(s)) < 200 else str(s)[:200] + "...")))
        st.dataframe(runs_display.drop(columns=["summary"]).rename(columns={"summary_short": "summary"}), use_container_width=True)

        # Expanded view with JSON and dry-run button
        for _, row in runs.iterrows():
            with st.expander(f"{row['run_name']} — {row.get('started_at')}"):
                st.write("Started:", row.get("started_at"))
                st.write("Finished:", row.get("finished_at"))
                try:
                    summary = json.loads(row["summary"]) if row["summary"] else row["summary"]
                except Exception:
                    summary = row["summary"]
                st.json(summary)
                st.button("Re-run preview (dry-run)", key=f"preview_{row.get('run_name')}_{row.get('started_at')}")


# ---------------------------------------------------------------------------


# ETF TRACKER
with tabs[2]:
    st.header("ETF Tracker")

    view_mode = st.radio("View Mode", ["By ETF", "By Date"], horizontal=True)

    if view_mode == "By ETF":
        # existing behavior (single ETF selection)
        etf_list = get_etf_list()
        if etf_list is None or etf_list.empty:
            st.info("No ETFs available in etf table.")
        else:
            etf_choices = (etf_list['etf_symbol'] + " — " + etf_list['etf_name'].fillna("")).tolist()
            etf_choice = st.selectbox("ETF", options=etf_choices)
            sel_symbol = etf_choice.split(" — ")[0]
            etf_id = int(etf_list[etf_list['etf_symbol'] == sel_symbol]['etf_id'].iloc[0])
            etf_history = get_etf_price_history(etf_id, days=365)
            if etf_history is not None and not etf_history.empty:
                # ensure proper column names (get_etf_price_history should canonicalize)
                st.plotly_chart(plot_candles(etf_history), use_container_width=True)
                st.dataframe(etf_history.tail(50).round(2))
            else:
                st.info("No transaction history found for this ETF.")

    else:
        # By Date view: show market summary for ETFs on a chosen date
        sel_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1), key="etf_date_input")
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
            st.dataframe(df.head(200).round(2))

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
                    st.dataframe(etf_history.tail(50).round(2))


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
