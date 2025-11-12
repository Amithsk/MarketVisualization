# ================================================================
# app.py — Streamlit Market Visualization Dashboard
# Updated: Intraday mini “Trade-of-the-day (Signals + Evaluation)” simplified
# NOTE: This file is based on your project app.py (preserved functions).
# ================================================================

import os
import sys
from pathlib import Path
import streamlit as st
import datetime
from datetime import date, timedelta
import pandas as pd
from io import StringIO
import json

# --- Ensure correct project import paths (parent of Code/)
# Add project root (D:\MarketVisualization) to Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Import project modules (unchanged)
from Code.queries import (
    get_nifty_recent, get_predictions, get_model_daily_summary,
    get_comparisons, get_intraday_for_symbol,
    get_intraday_by_date, get_gainers_losers, get_intraday_market_rows,
    get_intraday_top_value_traded, get_intraday_top_price_movers,
    get_intraday_summary_kpis, get_signal_summary_by_day_strategy,
    get_signals_by_date_strategy, get_feature_trends, get_strategy_runs,
    get_latest_prior_trading_date, get_smart_symbols,
    get_signals_for_date, get_strategy_features, get_latest_trade_date_from_bhavcopy,
    get_strategy_signals_for_date, get_signals_with_price_context,
    get_price_context_for_symbol, get_eval_tags_list, get_signals_with_eval_json,
    get_eval_tags_diff, get_etf_list, get_etf_price_history, get_etf_by_date
)
from Code.components import plot_candles, line_series, simple_bar, bar_with_labels, pie_split

# --- Streamlit setup ---
pd.options.display.float_format = "{:.2f}".format
st.set_page_config(layout="wide", page_title="Market Visualizations")
st.title("Market Visualizations")

tabs = st.tabs([
    "Market Overview",
    "Intraday Panel",
    "ETF Tracker",
    "Prediction & Model Health",
    "Trade-of-the-day"
])

# ================================================================
# Helper: Colorize intraday table
# ================================================================
def colorize_intraday_table(df: pd.DataFrame, decimals: int = 2):
    if df is None or df.empty:
        return df
    dfr = df.copy()
    num_cols = dfr.select_dtypes(include="number").columns.tolist()
    if num_cols:
        dfr[num_cols] = dfr[num_cols].round(decimals)

    def _row_color(row):
        if "direction" in row.index:
            if row["direction"] == "gain":
                return ["background-color: #e6ffe6"] * len(row)
            elif row["direction"] == "loss":
                return ["background-color: #ffe6e6"] * len(row)
        elif "pct_change" in row.index:
            try:
                val = float(row["pct_change"])
            except Exception:
                val = 0.0
            if val > 2:
                return ["background-color: #d9fcd9"] * len(row)
            elif val < -2:
                return ["background-color: #fcd9d9"] * len(row)
        return [""] * len(row)

    styler = dfr.style.apply(_row_color, axis=1)
    if num_cols:
        fmt = {c: f"{{:.{decimals}f}}" for c in num_cols}
        styler = styler.format(fmt)
    return styler


# ================================================================
# TAB 0 — MARKET OVERVIEW
# ================================================================
with tabs[0]:
    st.header("Market Overview — NIFTY")
    ndays = st.slider("Days to display", min_value=30, max_value=720, value=180)
    nifty_df = get_nifty_recent(days=ndays)
    st.subheader("NIFTY Price Chart (OHLC)")
    if nifty_df is not None and not nifty_df.empty:
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


# ================================================================
# TAB 1 — INTRADAY PANEL (preserved original logic)
# ================================================================
with tabs[1]:
    st.header("Intraday Panel")

    radio_mode = st.radio("Mode", ["By Symbol", "By Date"], horizontal=True)

    # default trade_date string used for functions that accept a date
    trade_date_str = None

    if radio_mode == "By Symbol":
        # By symbol mode — shows symbol history
        symbol = st.text_input("Symbol (exact)", value="RELIANCE.NS")
        days_intraday = st.slider("Days", 1, 365, 30)
        if symbol:
            intr = get_intraday_for_symbol(symbol, days=days_intraday)
            if intr is None or intr.empty:
                st.warning("No data for that symbol in intraday_bhavcopy. Confirm symbol.")
            else:
                intr = intr.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                                            "low": "Low", "close": "Close"})
                st.plotly_chart(plot_candles(intr), width='stretch')
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
            st.dataframe(df.head(100).round(2))

            st.subheader("Top 10 by Value Traded")
            if "net_trdval" in df.columns:
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
                    width='stretch',
                )

            st.subheader("Top 10 Price Movers (%)")
            if "open" in df.columns and "close" in df.columns:
                df_temp = df.copy()
                df_temp["pct_change"] = ((df_temp["close"] - df_temp["open"]) / df_temp["open"].replace(0, pd.NA)) * 100
                movers = df_temp.nlargest(10, "pct_change")[["symbol", "pct_change"]]
                st.plotly_chart(
                    bar_with_labels(
                        movers,
                        x_col="symbol",
                        y_col="pct_change",
                        title="Top 10 Price Movers (%)",
                        text_format=".2f",
                        max_items=10,
                    ),
                    width='stretch',
                )

        # --- KPIs (use selected trade_date if in By Date) ---
        kpi_data = get_intraday_summary_kpis(trade_date=trade_date_str)
        col1, col2, col3, col4, col5 = st.columns(5)
        try:
            col1.metric("Symbols Traded", kpi_data["symbols_traded"])
            col2.metric("Total Traded Value", f"{kpi_data['total_traded_value']:,0f}")
            col3.metric("Gainers", kpi_data["gainers"])
            col4.metric("Losers", kpi_data["losers"])
            col5.metric("Avg % Change", f"{kpi_data['avg_pct_change']}%")
        except Exception:
            # If kpi_data is missing keys, just skip showing them
            pass

        st.divider()

        # --- Market snapshot ---
        st.subheader("Market Snapshot")
        # If the By Date branch already fetched all rows (df), reuse it; otherwise call query
        if radio_mode == "By Date":
            intraday_df = df  # df was set above
        else:
            intraday_df = get_intraday_market_rows(trade_date=trade_date_str)

        if intraday_df is not None and not intraday_df.empty:
            st.dataframe(
                colorize_intraday_table(intraday_df),
                width='stretch',
                hide_index=True,
            )
        else:
            st.info("No intraday data available for the selected date.")

        st.divider()

        # --- Top 10 by traded value ---
        st.subheader("Top 10 Stocks by Traded Value (with 30-Day Average)")
        top_value_df = get_intraday_top_value_traded(trade_date=trade_date_str)
        if top_value_df is not None and not top_value_df.empty:
            st.dataframe(
                colorize_intraday_table(top_value_df),
                width='stretch',
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
                    width='stretch',
                    hide_index=True,
                )
            else:
                st.info("No gainers data for the selected date.")

        with col2:
            st.markdown("**Top Losers**")
            if losers_df is not None and not losers_df.empty:
                st.dataframe(
                    colorize_intraday_table(losers_df),
                    width='stretch',
                    hide_index=True,
                )
            else:
                st.info("No losers data for the selected date.")

        # ---------------------------
        # TRADE-OF-THE-DAY (Signals + Evaluation) — Intraday mini
        # Replaced dense table with compact summary and expanders for detail.
        # --- START: Intraday mini "Trade-of-the-day (Signals + Evaluation)" compact + expandable view ---
        st.subheader("Trade-of-the-day (Signals + Evaluation) — Intraday mini (compact)")

        intr_tod_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1), key="tod_date")

        eval_tags = get_eval_tags_list() or []
        default_tag = "intraday_v1_default" if "intraday_v1_default" in eval_tags else (eval_tags[0] if eval_tags else None)
        eval_options = ["(none)"] + eval_tags if eval_tags else ["(none)"]
        idx = 0
        if default_tag and default_tag in eval_tags:
            idx = eval_tags.index(default_tag) + 1
        eval_tag = st.selectbox("Eval Tag", options=eval_options, index=idx, help="Select evaluation run tag for labels", key="intr_eval_tag")

        # Filters row (compact)
        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        strategy_filter = f_col1.text_input("Strategy (exact)", value="", key="intr_strategy_filter")
        symbol_search = f_col2.text_input("Symbol contains", value="", key="intr_symbol_search")
        label_filter = f_col3.selectbox("Label filter", options=["All", "win", "loss", "neutral", "Not evaluated"], key="intr_label_filter")

        # Build filters for backend call
        page_size = 50
        filters = {}
        if strategy_filter:
            filters["strategy"] = strategy_filter
        if symbol_search:
            filters["symbol_search"] = symbol_search
        if label_filter and label_filter != "All":
            filters["label_outcome"] = "NOT_EVALUATED" if label_filter == "Not evaluated" else label_filter

        use_tag = eval_tag if eval_tag and eval_tag != "(none)" else ""

        # Fetch compact dataset (server returns {"meta":..., "rows":[...]} )
        data = {}
        try:
            data = get_signals_with_eval_json(intr_tod_date.strftime("%Y-%m-%d"), use_tag, limit=page_size, offset=0, filters=filters) or {}
        except Exception as e:
            st.error("Error fetching signals+evaluation data.")
            st.exception(e)
            data = {}

        meta = data.get("meta", {})
        rows = data.get("rows", []) or []
        df_rows = pd.DataFrame(rows)

        if df_rows.empty:
            st.info("No signal+evaluation data for this date/tag.")
        else:
            minimal_cols = [
                "signal_id", "symbol", "strategy", "signal_type",
                "signal_score", "entry_price", "target_price", "stop_price", "label_outcome", "ambiguous_flag"
            ]
            minimal_cols = [c for c in minimal_cols if c in df_rows.columns]

            # Normalize ambiguous flag to symbol-friendly mark
            if "ambiguous_flag" in df_rows.columns:
                # create Ambiguous column for display
                def _ambig(x):
                    try:
                        return "⚠" if int(x) == 1 else ""
                    except Exception:
                        return "⚠" if x else ""
                df_rows["Ambiguous"] = df_rows["ambiguous_flag"].apply(_ambig)
                # place Ambiguous after label_outcome if possible
                if "label_outcome" in minimal_cols:
                    minimal_cols = [c for c in minimal_cols if c != "ambiguous_flag"]
                    if "Ambiguous" not in minimal_cols:
                        try:
                            idx_label = minimal_cols.index("label_outcome")
                            minimal_cols.insert(idx_label + 1, "Ambiguous")
                        except ValueError:
                            minimal_cols.append("Ambiguous")

            display_df = df_rows[minimal_cols].copy()
            for col in ["signal_score", "entry_price", "target_price", "stop_price"]:
                if col in display_df.columns:
                    display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(2)

            # Show compact table
            st.dataframe(display_df.reset_index(drop=True), use_container_width=True, hide_index=True)

            # KPIs
            if meta:
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Rows", meta.get("total_rows", len(df_rows)))
                k2.metric("Wins", meta.get("wins", 0))
                k3.metric("Losses", meta.get("losses", 0))
                k4.metric("Win %", f"{meta.get('win_pct', 0):.1f}%" if meta.get("win_pct") else "-")

            st.markdown("---")
            st.write("### Detailed view — expand any row to inspect full signal + evaluation context")

            for i, row in df_rows.iterrows():
                header_label = f"{row.get('symbol', '-') } — {row.get('strategy', '-') } ({row.get('signal_type', '-')}) | Score: {row.get('signal_score', '-') }"
                with st.expander(header_label, expanded=False):
                    sig_fields = {
                        "Signal ID": row.get("signal_id"),
                        "Symbol": row.get("symbol"),
                        "Strategy": row.get("strategy"),
                        "Signal Type": row.get("signal_type"),
                        "Signal Score": row.get("signal_score"),
                        "Entry Price": row.get("entry_price"),
                        "Stop Price": row.get("stop_price"),
                        "Target Price": row.get("target_price"),
                        "Expected Hold (days)": row.get("expected_hold_days"),
                        "Entry Model": row.get("entry_model"),
                    }
                    st.write("**Signal details**")
                    st.table(pd.DataFrame(list(sig_fields.items()), columns=["Field", "Value"]))

                    st.write("**Evaluation details**")
                    eval_fields = {
                        "Eval Entry Price": row.get("eval_entry_price"),
                        "Eval Exit Price": row.get("eval_exit_price"),
                        "Eval Exit Date": row.get("eval_exit_date"),
                        "Label Outcome": row.get("label_outcome"),
                        "Notes": row.get("notes"),
                        "Eval Tag": row.get("eval_tag") or use_tag,
                    }
                    st.table(pd.DataFrame(list(eval_fields.items()), columns=["Field", "Value"]))

                    # Optional quick actions and intraday chart with overlays
                    a1, a2, a3 = st.columns([1, 1, 2])
                    with a1:
                        if st.button("Copy symbol", key=f"copy_sym_{i}"):
                            st.write(row.get("symbol"))
                    with a2:
                        if st.button("Open chart", key=f"open_chart_{i}"):
                            pass
                    with a3:
                        st.write("")

                    symbol = row.get("symbol")
                    if symbol:
                        try:
                            intr = get_intraday_for_symbol(symbol, days=30)
                            if intr is not None and not intr.empty:
                                intr = intr.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                                                            "low": "Low", "close": "Close"})
                                overlays = []
                                if pd.notna(row.get("entry_price")):
                                    overlays.append({"label": "entry", "price": float(row["entry_price"]), "dash": "dot", "color": "green"})
                                if pd.notna(row.get("stop_price")):
                                    overlays.append({"label": "stop", "price": float(row["stop_price"]), "dash": "dash", "color": "red"})
                                if pd.notna(row.get("target_price")):
                                    overlays.append({"label": "target", "price": float(row["target_price"]), "dash": "dashdot", "color": "blue"})
                                fig = plot_candles(intr, overlays=overlays, title=f"{symbol} — 30d Intraday Chart")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No intraday history available to plot for this symbol.")
                        except Exception as e:
                            st.warning("Could not fetch or plot intraday history for this symbol.")
                            st.exception(e)
        # --- END: Intraday mini "Trade-of-the-day (Signals + Evaluation)" compact + expandable view ---
        # --------------------------- end intraday Trade-of-the-day mini ---------------------------


# ================================================================
# TAB 2 — ETF TRACKER
# ================================================================
with tabs[2]:
    st.header("ETF Tracker")

    view_mode = st.radio("View Mode", ["By ETF", "By Date"], horizontal=True)

    if view_mode == "By ETF":
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
                st.plotly_chart(plot_candles(etf_history), width='stretch')
                st.dataframe(etf_history.tail(50).round(2))
            else:
                st.info("No transaction history found for this ETF.")

    else:
        sel_date = st.date_input("Trade Date", value=date.today() - timedelta(days=1), key="etf_date_input")
        date_str = sel_date.strftime("%Y-%m-%d")

        df = get_etf_by_date(date_str)
        if df is None or df.empty:
            st.info(f"No ETF transactions found for {date_str}.")
        else:
            st.subheader(f"ETF Market Summary — {date_str}")
            st.metric("ETFs traded", len(df))

            ycol = "TradedValue" if "TradedValue" in df.columns and df["TradedValue"].notna().any() else "Volume"

            st.plotly_chart(bar_with_labels(df, x_col="etf_symbol", y_col=ycol, title=f"Top ETFs by {ycol} on {date_str}", text_format=".0f", max_items=40), width='stretch')

            st.dataframe(df.head(200).round(2))

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
                    st.dataframe(etf_history.tail(50).round(2))


# ================================================================
# TAB 3 — PREDICTION & MODEL HEALTH
# ================================================================
with tabs[3]:
    st.header("Predictions & Model Health")
    models = get_model_daily_summary()
    model_names = models['model_name'].unique().tolist() if not models.empty else []
    chosen = st.selectbox("Model", options=["ALL"] + model_names)
    days = st.slider("Model history days", 7, 365, 90)
    if chosen == "ALL":
        summary = get_model_daily_summary(last_days=days)
    else:
        summary = get_model_daily_summary(model_name=chosen, last_days=days)
    st.subheader("Daily Summary")
    st.dataframe(summary)

    st.subheader("Forward Predictions (recent)")
    preds = get_predictions(model_name=None if chosen == "ALL" else chosen, only_forward=True, limit=200)
    st.dataframe(preds)

    st.subheader("Backtest Comparison (recent)")
    comp = get_comparisons(model_name=None if chosen == "ALL" else chosen, limit=200)
    st.dataframe(comp)


# ================================================================
# TAB 4 — TRADE-OF-THE-DAY (FULL)
# ================================================================
with tabs[4]:
    st.header("Trade-of-the-day — Signals & Details")

    # get default date (DB-first)
    default_date_iso = get_latest_trade_date_from_bhavcopy()
    if default_date_iso is None:
        st.error("Could not determine latest trading date from intraday_bhavcopy. Check DB and config.")
    else:
        # top controls (moved inside this tab only)
        left_col, right_col = st.columns([3, 1])
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
        if df_signals is None or df_signals.empty:
            st.info(f"No signals available for {chosen_date_iso}. Showing latest available data.")
        else:
            # Quick filters row
            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
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

            visible_cols = ["symbol", "strategy", "signal_type", "signal_score", "entry_model", "entry_price", "stop_price", "target_price", "expected_hold_days", "prev_close", "open"]
            visible_cols = [c for c in visible_cols if c in df_display.columns]
            st.dataframe(df_display[visible_cols].reset_index(drop=True), width='stretch')

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
        from_date = ft_col1.date_input("Start date", value=date.today() - timedelta(days=180), key="ft_start")
        to_date = ft_col1.date_input("End date", value=date.today() - timedelta(days=1), key="ft_end")
        start_str = from_date.strftime("%Y-%m-%d")
        end_str = to_date.strftime("%Y-%m-%d")

        chosen_symbol = None
        if mode_ft == "Smart":
            candidates = get_smart_symbols(end_str, lookback_days=5, top_k=20)
            if candidates is None or candidates.empty:
                st.info("No smart symbol suggestions found for this date. Try manual mode or change date range.")
            else:
                st.write("Top smart suggestions (pick one):")
                chosen_symbol = st.selectbox("Pick from suggestions", options=candidates["symbol"].tolist(), key="smart_sym_sel")
        else:
            manual_search = st.text_input("Type to filter symbols (contains)", value="", key="manual_sym_search")
            symbol_source = []
            # prefer df_signals if available (fixed usage: df_signals not signals_df)
            if 'df_signals' in locals() and isinstance(df_signals, pd.DataFrame) and not df_signals.empty:
                symbol_source = sorted(df_signals["symbol"].dropna().unique().tolist())
            if not symbol_source:
                intr_today = get_intraday_by_date(end_str)
                if intr_today is not None and not intr_today.empty:
                    symbol_source = sorted(intr_today["symbol"].dropna().unique().tolist())
            if manual_search:
                symbol_source = [s for s in symbol_source if manual_search.upper() in s.upper()]
            if symbol_source:
                chosen_symbol = st.selectbox("Choose symbol (manual)", options=["-- none --"] + symbol_source, key="manual_choose_sym")
                if chosen_symbol == "-- none --":
                    chosen_symbol = None
            else:
                chosen_symbol = None

        if chosen_symbol:
            try:
                feat_ts = get_strategy_features(chosen_symbol, start_date=start_str, end_date=end_str, features=None)
            except TypeError:
                try:
                    feat_ts = get_feature_trends(chosen_symbol, [], start_date=start_str, end_date=end_str)
                except Exception:
                    feat_ts = pd.DataFrame()

            if feat_ts is None or feat_ts.empty:
                st.warning("No feature data found for symbol / features in the selected range.")
            else:
                st.write(f"Showing features for {chosen_symbol} between {start_str} and {end_str}")
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
            runs_display = runs[["run_name", "started_at", "finished_at", "summary"]].copy()
            runs_display["summary_short"] = runs_display["summary"].apply(lambda s: (s if s is None else (s if len(str(s)) < 200 else str(s)[:200] + ".")))
            st.dataframe(runs_display.drop(columns=["summary"]).rename(columns={"summary_short": "summary"}), width='stretch')

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

# End of file
