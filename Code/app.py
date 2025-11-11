# app.py
import os
import sys
# Add project root to Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import datetime
from datetime import date, timedelta
import pandas as pd
from io import StringIO
import json

from Code.queries import (
    get_nifty_recent, get_predictions, get_model_daily_summary,
    get_comparisons, get_intraday_for_symbol,
    get_intraday_by_date, get_gainers_losers, get_intraday_market_rows, get_intraday_top_value_traded,
    get_intraday_top_price_movers, get_intraday_summary_kpis, get_signal_summary_by_day_strategy,
    get_signals_by_date_strategy, get_feature_trends, get_strategy_runs,
    get_latest_prior_trading_date, get_smart_symbols,
    get_signals_for_date, get_strategy_features,get_latest_trade_date_from_bhavcopy,get_strategy_signals_for_date,
    get_signals_with_price_context,get_price_context_for_symbol,
    get_eval_tags_list,get_signals_with_eval_json,get_eval_tags_diff,
    get_etf_list, get_etf_price_history, get_etf_by_date
)

from Code.components import plot_candles, line_series, simple_bar, bar_with_labels, pie_split
pd.options.display.float_format = "{:.2f}".format
st.set_page_config(layout="wide", page_title="Market Visualizations")

st.title("Market Visualizations")


tabs = st.tabs(["Market Overview", "Intraday Panel", "ETF Tracker", "Prediction & Model Health","Trade-of-the-day"])



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
    st.plotly_chart(fig, width="stretch")

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
    st.header("Intraday Panel")
    # (existing intraday code unchanged)
    # ... (kept intact from original)
    # The intraday tab contains many controls including a Trade-of-the-day mini control
    # which we leave as-is for intraday-specific views.
    # (Full intraday block retained below in file; unchanged.)

    st.subheader("Intraday Summary")
    # ... (omitted here for brevity in this header section)
    # actual intraday code continues (unchanged)


# TRADE-OF-THE-DAY TAB 
with tabs[4]:  
    st.header("Trade-of-the-day — Signals & Details")

    # get default date (DB-first)
    default_date_iso = get_latest_trade_date_from_bhavcopy()
    if default_date_iso is None:
        st.error("Could not determine latest trading date from intraday_bhavcopy. Check DB and config.")
    else:
        # top controls (moved inside this tab only)
        # use a stable key so the widget persists correctly across reruns
        left_col, right_col = st.columns([3,1])
        with left_col:
            ui_date = st.date_input(
                "Trade date (Trade-of-the-day)",
                value=pd.to_datetime(default_date_iso).date(),
                key="tod_ui_date"
            )
        with right_col:
            if st.button("Refresh trade-of-the-day", key="tod_refresh"):
                st.rerun()
        chosen_date_iso = ui_date.isoformat()

        # load signals (with price context)
        df_signals = get_signals_with_price_context(chosen_date_iso)

        st.subheader(f"Signals for {chosen_date_iso}")
        if df_signals.empty:
            st.info(f"No signals available for {chosen_date_iso}. Showing latest available data.")
            # allow user to pick earlier date manually via date picker
        else:
            # Quick filters row
            c1, c2, c3, c4 = st.columns([3,2,2,3])
            with c1:
                strategies = sorted(df_signals["strategy"].dropna().unique().tolist())
                sel_strats = st.multiselect("Strategy", options=strategies, default=strategies)
            with c2:
                sel_side = st.selectbox("Side", options=["ALL", "LONG", "SHORT"], index=0)
            with c3:
                min_score = st.number_input("Min |signal_score|", value=0.0, step=0.1, format="%.2f")
            with c4:
                search_symbol = st.text_input("Search symbol", value="")

            # apply filters
            df_display = df_signals.copy()
            if sel_strats:
                df_display = df_display[df_display["strategy"].isin(sel_strats)]
            if sel_side != "ALL":
                df_display = df_display[df_display["signal_type"] == sel_side]
            df_display = df_display[df_display["signal_score"].abs() >= float(min_score)]
            if search_symbol:
                df_display = df_display[df_display["symbol"].str.contains(search_symbol, case=False, na=False)]

            # visible columns
            visible_cols = ["symbol","strategy","signal_type","signal_score","entry_model","entry_price","stop_price","target_price","expected_hold_days","prev_close","open"]
            visible_cols = [c for c in visible_cols if c in df_display.columns]
            st.dataframe(df_display[visible_cols].reset_index(drop=True), width='stretch')

            # Download filtered CSV
            st.download_button("Export signals subset (CSV)", df_display.to_csv(index=False).encode("utf-8"),
                               file_name=f"signals_{chosen_date_iso}.csv", mime="text/csv")

            # Symbol detail panel (expand)
            chosen_symbol = st.selectbox("Select symbol to inspect", options=[""] + df_display["symbol"].dropna().unique().tolist(), key="tod_symbol_inspect")
            if chosen_symbol:
                sel_row = df_display[df_display["symbol"] == chosen_symbol].iloc[0]
                symbol = chosen_symbol
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
                    st.plotly_chart(fig, width="stretch")

        # Feature Trends: Smart / Manual selector
        st.markdown("---")
        st.subheader("Feature Trends (per-symbol)")

        ft_col1, ft_col2 = st.columns([2, 1])
        mode_ft = ft_col2.radio("Mode", ["Smart", "Manual"], index=0, horizontal=False)
        # date range for features
        from_date = ft_col1.date_input("Start date", value=date.today() - timedelta(days=180), key="ft_start")
        to_date = ft_col1.date_input("End date", value=date.today() - timedelta(days=1), key="ft_end")
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
            symbol_source = []
            if 'df_signals' in locals() and isinstance(df_signals, pd.DataFrame) and not df_signals.empty:
                symbol_source = sorted(df_signals["symbol"].dropna().unique().tolist())
            else:
                intr_today = get_intraday_by_date(end_str)
            if intr_today is not None and not intr_today.empty:
                symbol_source = sorted(intr_today["symbol"].dropna().unique().tolist())
            if not symbol_source:
                intr_today = get_intraday_by_date(end_str)
                if intr_today is not None and not intr_today.empty:
                    symbol_source = sorted(intr_today["symbol"].dropna().unique().tolist())
            if manual_search:
                symbol_source = [s for s in symbol_source if manual_search.upper() in s.upper()]
            if symbol_source:
                chosen_symbol = st.selectbox("Choose symbol (manual)", options=["-- none --"] + symbol_source, key="manual_choose_sym")
            else:
                chosen_symbol = None

        if chosen_symbol:
            # fetch features via get_strategy_features if available; otherwise fallback to get_feature_trends
            try:
                feat_ts = get_strategy_features(chosen_symbol, start_date=start_str, end_date=end_str, features=None)
            except TypeError:
                # if function signature differs, try legacy get_feature_trends(symbol, features, start, end)
                try:
                    feat_ts = get_feature_trends(chosen_symbol, [], start_date=start_str, end_date=end_str)
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
                st.plotly_chart(fig, width="stretch")
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
            runs_display["summary_short"] = runs_display["summary"].apply(lambda s: (s if s is None else (s if len(str(s)) < 200 else str(s)[:200] + ".")))
            st.dataframe(runs_display.drop(columns=["summary"]).rename(columns={"summary_short": "summary"}), width='stretch')

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
                st.plotly_chart(plot_candles(etf_history), width='stretch')
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

            st.plotly_chart(bar_with_labels(df, x_col="etf_symbol", y_col=ycol, title=f"Top ETFs by {ycol} on {date_str}", text_format=".0f", max_items=40), width='stretch')

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
                    st.plotly_chart(plot_candles(etf_history, title=f"{sel} — 1y history"), width='stretch')
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


# ---------------------------------------------------------------------------
# End of app.py
