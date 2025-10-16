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
        q = "SELECT symbol, pct_change FROM gainers_losers WHERE trade_date = :td ORDER BY pct_change DESC LIMIT :n"
        params = {"td": on_date, "n": top_n}
        df = read_sql("intraday", q, params=params)
    else:
        q = "SELECT trade_date, symbol, pct_change FROM gainers_losers ORDER BY trade_date DESC LIMIT :n"
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

# ---------- Intraday functions (drop-in replacements) ----------

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


