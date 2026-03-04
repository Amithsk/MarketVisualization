# =========================================================
# File: backend/app/services/nifty_stock_data_service.py
# =========================================================

from datetime import date, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging


logger = logging.getLogger(__name__)

# =========================================================
# TRADING DATE UTILITIES
# =========================================================

def _get_previous_trading_date(db: Session, trade_date: date) -> date:
    """
    Returns the most recent trading date before the given trade_date.
    """
    sql = text("""
        SELECT MAX(trade_date) AS prev_trade_date
        FROM intraday_bhavcopy
        WHERE trade_date < :trade_date
    """)

    row = db.execute(sql, {"trade_date": trade_date}).fetchone()
    return row[0] if row and row[0] else None


# =========================================================
# UNIVERSE LOADER
# =========================================================

def get_universe_symbols(db: Session) -> List[str]:
    """
    Returns all symbols eligible for Step-3
    (include_in_bhav = 1)
    """

    sql = text("""
        SELECT symbol
        FROM instruments_master
        WHERE include_in_bhav = 1
    """)

    rows = db.execute(sql).fetchall()
    symbols = [r[0] for r in rows]

    logger.info("[MARKET_DATA][STATE][UNIVERSE_FETCHED] count=%s", len(symbols))

    return symbols


# =========================================================
# 20-DAY AVERAGE TRADED VALUE
# =========================================================

def get_avg_traded_value_20d(
    db: Session,
    trade_date: date,
    symbols: List[str],
) -> Dict[str, float]:
    """
    Returns {symbol: avg_20d_net_trdval}
    """

    # nothing to do if no symbols requested
    if not symbols:
        return {}

    # Step 1: Get last 20 trading dates before the provided date
    date_sql = text("""
        SELECT DISTINCT trade_date
        FROM intraday_bhavcopy
        WHERE trade_date < :trade_date
        ORDER BY trade_date DESC
        LIMIT 20
    """)

    date_rows = db.execute(date_sql, {"trade_date": trade_date}).fetchall()
    last_20_dates = [r[0] for r in date_rows]

    if not last_20_dates:
        # no history available yet
        return {}

    # Step 2: Calculate average net traded value over those dates
    sql = text("""
        SELECT symbol, AVG(net_trdval) AS avg_20d
        FROM intraday_bhavcopy
        WHERE trade_date IN :last_20_dates
          AND symbol IN :symbols
        GROUP BY symbol
    """)

    rows = db.execute(sql, {
        "last_20_dates": tuple(last_20_dates),
        "symbols": tuple(symbols),
    }).fetchall()

    result = {r[0]: float(r[1] or 0) for r in rows}

    logger.info(
        "[MARKET_DATA][STATE][AVG20D_FETCHED] trade_date=%s count=%s",
        trade_date,
        len(result),
    )

    return result


# =========================================================
# ATR FETCH (FROM strategy_features)
# =========================================================

def get_atr_14_for_date(
    db: Session,
    trade_date: date,
    symbols: List[str],
) -> Dict[str, float]:
    """
    Returns {symbol: atr_14}
    """

    if not symbols:
        return {}

    previous_trading_date = _get_previous_trading_date(db, trade_date)
    if not previous_trading_date:
        return {}

    sql = text("""
        SELECT symbol, value
        FROM strategy_features
        WHERE trade_date = :previous_trading_date
          AND feature_name = 'atr_14'
          AND symbol IN :symbols
    """)

    rows = db.execute(sql, {
        "previous_trading_date": previous_trading_date,
        "symbols": tuple(symbols),
    }).fetchall()

    result = {r[0]: float(r[1] or 0) for r in rows}

    logger.info(
        "[MARKET_DATA][STATE][ATR_FETCHED] trade_date=%s count=%s",
        trade_date,
        len(result),
    )

    return result


# =========================================================
# YESTERDAY CANDLE FETCH
# =========================================================

def get_yesterday_candles(
    db: Session,
    trade_date: date,
    symbols: List[str],
) -> Dict[str, Dict[str, float]]:
    """
    Returns:
    {
        symbol: {
            "high": float,
            "low": float,
            "close": float
        }
    }
    """

    if not symbols:
        return {}

    #yesterday = trade_date - timedelta(days=1)
    yesterday = _get_previous_trading_date(db, trade_date)
    if not yesterday:
        return {}

    sql = text("""
        SELECT symbol, high, low, close
        FROM intraday_bhavcopy
        WHERE trade_date = :yesterday
          AND symbol IN :symbols
    """)

    rows = db.execute(sql, {
        "yesterday": yesterday,
        "symbols": tuple(symbols),
    }).fetchall()

    result = {
        r[0]: {
            "high": float(r[1] or 0),
            "low": float(r[2] or 0),
            "close": float(r[3] or 0),
        }
        for r in rows
    }

    logger.info(
        "[MARKET_DATA][STATE][YESTERDAY_CANDLE_FETCHED] trade_date=%s count=%s",
        yesterday,
        len(result),
    )

    return result


# =========================================================
# WRAPPER FUNCTIONS (ADDED — DO NOT REMOVE ORIGINALS)
# =========================================================
# These wrappers align with step3_service expected names.
# Core logic is untouched.

def fetch_universe_symbols(db: Session) -> List[str]:
    return get_universe_symbols(db)


def fetch_20d_trdval_bulk(
    db: Session,
    trade_date: date,
    symbols: List[str],
) -> Dict[str, float]:
    return get_avg_traded_value_20d(db, trade_date, symbols)


def fetch_atr_bulk(
    db: Session,
    trade_date: date,
    symbols: List[str],
) -> Dict[str, float]:
    return get_atr_14_for_date(db, trade_date, symbols)


def fetch_yesterday_candles(
    db: Session,
    trade_date: date,
    symbols: List[str],
) -> Dict[str, Dict[str, float]]:
    return get_yesterday_candles(db, trade_date, symbols)



