# queries.py
# High-level query functions that target the correct DB via db.read_sql(db_key, ...)

from db import read_sql
import pandas as pd

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


