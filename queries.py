# queries.py
# High-level query functions that target the correct DB via db.read_sql(db_key, ...)

from db import read_sql
import pandas as pd
from datetime import datetime, timedelta, date

# ---------- NIFTY (db_key = 'nifty') ----------
def get_nifty_recent(days: int = 180):
    q = """
    SELECT `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, SMA_5, SMA_20, RSI, ATR
    FROM nifty_prices
    ORDER BY `Date` DESC
    LIMIT :limit
    """
    df = read_sql("nifty", q, params={"limit": days})
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
    return df

def get_predictions(model_name: str = None, only_forward: bool = True, limit: int = 500):
    where_clause = "WHERE is_forward = 1" if only_forward else ""
    if model_name:
        where_clause = f"{where_clause} AND model_name = :model_name" if where_clause else "WHERE model_name = :model_name"
    q = f"""
    SELECT date, model_name, predicted_dir, predicted_price, is_forward
    FROM predictions
    {where_clause}
    ORDER BY date DESC
    LIMIT :limit
    """
    df = read_sql("nifty", q, params={"model_name": model_name, "limit": limit})
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    return df

def get_model_daily_summary(model_name: str = None, last_days: int = 90):
    and_model = "AND model_name = :model_name" if model_name else ""
    q = f"""
    SELECT summary_date, model_name, total_bars, correct, incorrect, accuracy_pct, avg_error_mag
    FROM model_daily_summary
    WHERE summary_date >= CURDATE() - INTERVAL :days DAY
    {and_model}
    ORDER BY summary_date
    """
    df = read_sql("nifty", q, params={"days": last_days, "model_name": model_name})
    if not df.empty:
        df["summary_date"] = pd.to_datetime(df["summary_date"])
    return df

def get_comparisons(model_name: str = None, limit: int = 500):
    where = "WHERE model_name = :model_name" if model_name else ""
    q = f"""
    SELECT date, model_name, actual_dir, predicted_dir, was_correct, error_mag
    FROM comparisons
    {where}
    ORDER BY date DESC
    LIMIT :limit
    """
    df = read_sql("nifty", q, params={"model_name": model_name, "limit": limit})
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

# ---------- INTRADAY (db_key = 'intraday') ----------
def get_intraday_for_symbol(symbol: str, days: int = 30):
    q = """
    SELECT trade_date, symbol, open, high, low, close, net_trdval, net_trdqty
    FROM intraday_bhavcopy
    WHERE symbol = :symbol
      AND trade_date >= CURDATE() - INTERVAL :days DAY
    ORDER BY trade_date
    """
    df = read_sql("intraday", q, params={"symbol": symbol, "days": days})
    if not df.empty:
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df

def get_gainers_losers(on_date: str = None, top_n: int = 10):
    if on_date:
        q = "SELECT symbol, pct_change FROM gainer_loser WHERE trade_date = :td ORDER BY pct_change DESC LIMIT :n"
        params = {"td": on_date, "n": top_n}
        df = read_sql("intraday", q, params=params)
    else:
        q = "SELECT trade_date, symbol, pct_change FROM gainer_loser ORDER BY trade_date DESC LIMIT :n"
        df = read_sql("intraday", q, params={"n": top_n})
    if not df.empty and "trade_date" in df.columns:
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def get_intraday_by_date(trade_date: str):
    """
    Returns summary of all stocks traded on a given date.
    Columns: symbol, open, high, low, close, net_trdval, net_trdqty
    """
    q = """
    SELECT trade_date, symbol, open, high, low, close, net_trdval, net_trdqty
    FROM intraday_bhavcopy
    WHERE trade_date = :td
    ORDER BY net_trdval DESC
    LIMIT 200
    """
    return read_sql("intraday", q, params={"td": trade_date})



def get_intraday_market_rows(trade_date: str = None) -> pd.DataFrame:
    """
    Return intraday rows for trade_date ordered by net_trdval desc.
    Columns returned include: trade_date, symbol, open, high, low, close, net_trdval, net_trdqty, pct_change, direction
    """
    if trade_date is None:
        trade_date = datetime.now().date().isoformat()

    q = """
    SELECT
        trade_date,
        symbol,
        open,
        high,
        low,
        close,
        net_trdval,
        net_trdqty,
        ROUND((close - open) / NULLIF(open,0) * 100, 2) AS pct_change,
        CASE
            WHEN close > open THEN 'gain'
            WHEN close < open THEN 'loss'
            ELSE 'flat'
        END AS direction
    FROM intraday_bhavcopy
    WHERE trade_date = :trade_date
    ORDER BY net_trdval DESC
    """
    df = read_sql("intraday", q, params={"trade_date": trade_date})
    # ensure consistent dtypes (match other functions' style)
    if not df.empty:
        if "trade_date" in df.columns:
            df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def get_intraday_top_value_traded(trade_date: str = None, lookback_days: int = 30, limit: int = 10) -> pd.DataFrame:
    """
    Top N symbols by traded value for trade_date, plus avg_30d_net_trdval over lookback_days (inclusive).
    Returns DataFrame with columns: symbol, open, close, net_trdval, pct_change, avg_30d_net_trdval
    """
    if trade_date is None:
        td = datetime.now().date()
    else:
        # accept date string or date object
        try:
            td = datetime.fromisoformat(trade_date).date()
        except Exception:
            td = datetime.strptime(str(trade_date), "%Y-%m-%d").date()
    trade_date_str = td.isoformat()
    start_date_str = (td - timedelta(days=lookback_days - 1)).isoformat()

    q = f"""
    WITH top_symbols AS (
        SELECT symbol
        FROM intraday_bhavcopy
        WHERE trade_date = :trade_date
        ORDER BY net_trdval DESC
        LIMIT :limit
    )
    SELECT
        t.symbol,
        i.open,
        i.close,
        i.net_trdval,
        ROUND((i.close - i.open) / NULLIF(i.open,0) * 100, 2) AS pct_change,
        ROUND((
            SELECT AVG(net_trdval)
            FROM intraday_bhavcopy
            WHERE symbol = t.symbol
              AND trade_date BETWEEN :start_date AND :trade_date
        ), 2) AS avg_30d_net_trdval
    FROM top_symbols t
    JOIN intraday_bhavcopy i
      ON i.symbol = t.symbol
     AND i.trade_date = :trade_date
    ORDER BY i.net_trdval DESC
    """
    df = read_sql("intraday", q, params={"trade_date": trade_date_str, "start_date": start_date_str, "limit": limit})
    return df


def get_intraday_top_price_movers(
    trade_date: str = None, limit: int = 10
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns tuple (gainers_df, losers_df) for the given trade_date.
    Each DataFrame columns: symbol, open, close, pct_change, net_trdval
    """
    if trade_date is None:
        trade_date = datetime.now().date().isoformat()

    q_gainers = """
    SELECT
        symbol,
        open,
        close,
        ROUND((close - open) / NULLIF(open,0) * 100, 2) AS pct_change,
        net_trdval
    FROM intraday_bhavcopy
    WHERE trade_date = :trade_date
    ORDER BY pct_change DESC
    LIMIT :limit
    """
    q_losers = """
    SELECT
        symbol,
        open,
        close,
        ROUND((close - open) / NULLIF(open,0) * 100, 2) AS pct_change,
        net_trdval
    FROM intraday_bhavcopy
    WHERE trade_date = :trade_date
    ORDER BY pct_change ASC
    LIMIT :limit
    """

    gainers = read_sql("intraday", q_gainers, params={"trade_date": trade_date, "limit": limit})
    losers = read_sql("intraday", q_losers, params={"trade_date": trade_date, "limit": limit})

    return gainers, losers


def get_intraday_summary_kpis(trade_date: str = None) -> dict:
    """
    Return summary KPIs for intraday market snapshot for trade_date.
    Output dict keys:
      symbols_traded, total_traded_value, gainers, losers, flat, avg_pct_change
    """
    if trade_date is None:
        trade_date = datetime.now().date().isoformat()

    q = """
    SELECT
        COUNT(*) AS symbols_traded,
        ROUND(SUM(net_trdval), 2) AS total_traded_value,
        SUM(CASE WHEN close > open THEN 1 ELSE 0 END) AS gainers,
        SUM(CASE WHEN close < open THEN 1 ELSE 0 END) AS losers,
        SUM(CASE WHEN close = open THEN 1 ELSE 0 END) AS flat,
        ROUND(AVG((close - open) / NULLIF(open,0) * 100), 2) AS avg_pct_change
    FROM intraday_bhavcopy
    WHERE trade_date = :trade_date
    """
    df = read_sql("intraday", q, params={"trade_date": trade_date})
    if df.empty:
        return {"symbols_traded": 0, "total_traded_value": 0.0, "gainers": 0, "losers": 0, "flat": 0, "avg_pct_change": 0.0}

    row = df.iloc[0].to_dict()
    # coerce types to native
    return {
        "symbols_traded": int(row.get("symbols_traded") or 0),
        "total_traded_value": float(row.get("total_traded_value") or 0.0),
        "gainers": int(row.get("gainers") or 0),
        "losers": int(row.get("losers") or 0),
        "flat": int(row.get("flat") or 0),
        "avg_pct_change": float(row.get("avg_pct_change") or 0.0),
    }

# --- New: Strategy / Signals / Features / Runs (db_key = 'intraday') ---

def get_signal_summary_by_day_strategy(last_days: int = 30):
    """
    Returns daily counts by strategy and LONG/SHORT breakdown for the past `last_days`.
    Columns: d (date), strategy, c (count), longs, shorts
    """
    q = """
    SELECT DATE(trade_date) AS d,
           strategy,
           COUNT(*) AS c,
           SUM(signal_type = 'LONG') AS longs,
           SUM(signal_type = 'SHORT') AS shorts
    FROM strategy_signals
    WHERE trade_date >= CURDATE() - INTERVAL :days DAY
    GROUP BY DATE(trade_date), strategy
    ORDER BY DATE(trade_date) DESC, strategy
    """
    df = read_sql("intraday", q, params={"days": last_days})
    if not df.empty:
        df["d"] = pd.to_datetime(df["d"])
    return df


def get_signals_by_date_strategy(trade_date: str, strategy: str = None, limit: int = 1000):
    """
    Return detailed signals for a date (optionally filter by strategy).
    """
    if strategy:
        q = """
        SELECT trade_date, strategy, symbol, signal_type, signal_score,
               entry_price, stop_price, target_price, expected_hold_days,
               params, notes, created_at
        FROM strategy_signals
        WHERE trade_date = :td AND strategy = :strategy
        ORDER BY signal_score DESC
        LIMIT :limit
        """
        params = {"td": trade_date, "strategy": strategy, "limit": limit}
    else:
        q = """
        SELECT trade_date, strategy, symbol, signal_type, signal_score,
               entry_price, stop_price, target_price, expected_hold_days,
               params, notes, created_at
        FROM strategy_signals
        WHERE trade_date = :td
        ORDER BY signal_score DESC
        LIMIT :limit
        """
        params = {"td": trade_date, "limit": limit}

    df = read_sql("intraday", q, params=params)
    if not df.empty:
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def get_feature_trends(symbol: str, feature_names: list, start_date: str = None, end_date: str = None):
    """
    Pull feature time series for a symbol. Returns pivoted DataFrame:
    Index: trade_date, Columns: feature names
    - feature_names: list of strings (e.g., ['rsi_14','atr_14'])
    - start_date / end_date: 'YYYY-MM-DD' strings or None
    """
    if not feature_names:
        return pd.DataFrame()

    # build IN clause safely by generating params
    placeholders = ", ".join([f":f{i}" for i in range(len(feature_names))])
    params = {"symbol": symbol}
    for i, fn in enumerate(feature_names):
        params[f"f{i}"] = fn

    date_clause = ""
    if start_date and end_date:
        date_clause = "AND trade_date BETWEEN :start_date AND :end_date"
        params["start_date"] = start_date
        params["end_date"] = end_date
    elif start_date:
        date_clause = "AND trade_date >= :start_date"
        params["start_date"] = start_date
    elif end_date:
        date_clause = "AND trade_date <= :end_date"
        params["end_date"] = end_date

    q = f"""
    SELECT trade_date, feature_name, value
    FROM strategy_features
    WHERE symbol = :symbol
      AND feature_name IN ({placeholders})
      {date_clause}
    ORDER BY trade_date
    """
    df = read_sql("intraday", q, params=params)
    if df.empty:
        return df

    df["trade_date"] = pd.to_datetime(df["trade_date"])
    # pivot to time-series: rows=trade_date, cols=feature_name
    pivot = df.pivot_table(index="trade_date", columns="feature_name", values="value", aggfunc="first")
    pivot = pivot.sort_index()
    return pivot


def get_strategy_runs(limit: int = 50):
    """
    Return recent rows from strategy_runs table.
    Columns: run_name, started_at, finished_at, summary (JSON)
    """
    q = """
    SELECT run_name, started_at, finished_at, summary
    FROM strategy_runs
    ORDER BY started_at DESC
    LIMIT :limit
    """
    df = read_sql("intraday", q, params={"limit": limit})
    if not df.empty:
        df["started_at"] = pd.to_datetime(df["started_at"])
        df["finished_at"] = pd.to_datetime(df["finished_at"])
    return df


# --- new helpers for Signals / Features / Runs (append into queries.py) ---
from db import read_sql
import pandas as pd
from datetime import datetime, timedelta

def get_latest_prior_trading_date(selected_date: str):
    """
    Return the MAX(trade_date) <= selected_date from intraday_bhavcopy.
    selected_date: 'YYYY-MM-DD' or date-like string
    """
    q = """
    SELECT MAX(trade_date) AS latest
    FROM intraday_bhavcopy
    WHERE trade_date <= :d
    """
    df = read_sql("intraday", q, params={"d": selected_date})
    if df is None or df.empty or df.loc[0, "latest"] is None:
        return None
    return pd.to_datetime(df.loc[0, "latest"]).date().isoformat()


def get_smart_symbols(selected_date: str, lookback_days: int = 5, top_k: int = 10):
    """
    Return top-K candidate symbols based on:
      - completeness of features on selected_date (count of non-null feature_name)
      - recent presence in strategy_signals in last `lookback_days`
    Returns DataFrame: symbol, feature_count, recent_signals_count, score
    """
    # 1) count features on selected_date
    q_features = """
    SELECT symbol, COUNT(*) AS feature_count
    FROM strategy_features
    WHERE trade_date = :d
      AND value IS NOT NULL
    GROUP BY symbol
    """
    df_feat = read_sql("intraday", q_features, params={"d": selected_date})
    if df_feat is None:
        df_feat = pd.DataFrame(columns=["symbol", "feature_count"])

    # 2) recent signals
    since = (pd.to_datetime(selected_date) - timedelta(days=lookback_days)).date().isoformat()
    q_signals = """
    SELECT symbol, COUNT(*) AS recent_signals
    FROM strategy_signals
    WHERE trade_date BETWEEN :since AND :d
    GROUP BY symbol
    """
    df_sig = read_sql("intraday", q_signals, params={"since": since, "d": selected_date})
    if df_sig is None:
        df_sig = pd.DataFrame(columns=["symbol", "recent_signals"])

    # merge and compute score
    df = pd.merge(df_feat, df_sig, on="symbol", how="outer").fillna(0)
    df["feature_count"] = df["feature_count"].astype(int)
    df["recent_signals"] = df["recent_signals"].astype(int)
    # score: weight features higher
    df["score"] = df["feature_count"] * 3 + df["recent_signals"]
    df = df.sort_values("score", ascending=False).head(top_k)
    return df.reset_index(drop=True)


def get_signals_for_date(trade_date: str, strategies=None, signal_types=None, min_score: float=None, symbol_like=None, limit: int = 1000):
    """
    Fetch signals filtered by the UI inputs.
    Returns signals with JSON notes column if present.
    """
    where = ["signal_date = :td"]
    params = {"td": trade_date, "limit": limit}
    if strategies:
        where.append("strategy IN (:strategies)")
        params["strategies"] = strategies
    if signal_types:
        where.append("signal_type IN (:signal_types)")
        params["signal_types"] = signal_types
    if min_score is not None:
        where.append("signal_score >= :min_score")
        params["min_score"] = min_score
    if symbol_like:
        where.append("symbol LIKE :sym")
        params["sym"] = f"%{symbol_like}%"

    where_clause = " AND ".join(where)
    q = f"""
    SELECT signal_date, strategy, symbol, signal_type, signal_score,
           entry_price, stop_price, target_price, expected_hold_days, notes
    FROM strategy_signals
    WHERE {where_clause}
    ORDER BY signal_score DESC
    LIMIT :limit
    """
    df = read_sql("intraday", q, params=params)
    if not df.empty and "signal_date" in df.columns:
        df["signal_date"] = pd.to_datetime(df["signal_date"])
    return df


def get_strategy_features(symbol: str, start_date: str, end_date: str, features: list = None):
    """
    Fetch time-series of selected features for a symbol between start_date and end_date.
    Assumes columns: trade_date, symbol, feature_name, feature_value as Value
    Returns pivoted DataFrame with index=trade_date and columns=feature names.
    """
    q = """
    SELECT trade_date, symbol, feature_name, value AS feature_value
    FROM strategy_features
    WHERE symbol = :symbol
      AND trade_date BETWEEN :start_date AND :end_date
    ORDER BY trade_date
    """
    df = read_sql("intraday", q, params={"symbol": symbol, "start_date": start_date, "end_date": end_date})
    if df is None or df.empty:
        return pd.DataFrame()
    # pivot into wide form
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df_p = df.pivot_table(index="trade_date", columns="feature_name", values="feature_value", aggfunc="first")
    if features:
        sel = [f for f in features if f in df_p.columns]
        df_p = df_p[sel]
    df_p = df_p.sort_index()
    return df_p


def get_strategy_runs(limit: int = 50):
    """
    Fetch latest runs from strategy_runs for display in the UI.
    Columns: id, run_name, started_at, finished_at, summary (JSON/text)
    """
    q = """
    SELECT id, run_name, started_at, finished_at, summary
    FROM strategy_runs
    ORDER BY started_at DESC
    LIMIT :limit
    """
    df = read_sql("intraday", q, params={"limit": limit})
    if not df.empty and "started_at" in df.columns:
        df["started_at"] = pd.to_datetime(df["started_at"])
    return df


# ---------- ETF (db_key = 'etf') ----------
def get_etf_list():
    q = "SELECT etf_id, etf_symbol, etf_name, etf_fundhouse_name FROM etf ORDER BY etf_symbol"
    df = read_sql("etf", q)
    return df

# queries.py (updated get_etf_price_history)
def get_etf_price_history(etf_id: int, days: int = 365):
    q = """
    SELECT etf_trade_date as trade_date,
           etf_last_traded_price as close,
           etf_traded_high as high,
           etf_traded_low as low,
           etf_day_open as open,
           etf_daily_traded_volume as volume
    FROM etf_daily_transaction
    WHERE etf_id = :etf_id
      AND etf_trade_date >= CURDATE() - INTERVAL :days DAY
    ORDER BY etf_trade_date
    """
    df = read_sql("etf", q, params={"etf_id": etf_id, "days": days})
    if df.empty:
        return df
    # canonicalize column names to what UI expects
    df = df.rename(columns={
        "trade_date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def get_etf_by_date(trade_date: str, limit: int = 200):
    """
    Return ETF price/volume rows for a given trade date.
    Columns returned: etf_id, etf_symbol, etf_name, etf_last_traded_price AS close,
                      etf_day_open AS open, etf_traded_high AS high, etf_traded_low AS low,
                      etf_daily_traded_volume AS volume, etf_daily_traded_value AS traded_value (if exists)
    """
    q = """
    SELECT d.etf_id,
           e.etf_symbol,
           e.etf_name,
           d.etf_last_traded_price AS close,
           d.etf_day_open AS open,
           d.etf_traded_high AS high,
           d.etf_traded_low AS low,
           d.etf_daily_traded_volume AS volume,
           d.etf_daily_traded_value AS traded_value
    FROM etf_daily_transaction d
    JOIN etf e ON d.etf_id = e.etf_id
    WHERE d.etf_trade_date = :td
    ORDER BY d.etf_daily_traded_value DESC
    LIMIT :limit
    """
    df = read_sql("etf", q, params={"td": trade_date, "limit": limit})
    if not df.empty:
        # canonicalize names for UI
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
            "traded_value": "TradedValue",
            "etf_trade_date": "Date"
        })
    return df


