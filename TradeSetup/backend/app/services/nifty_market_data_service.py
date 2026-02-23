#backend/app/services/nifty_market_data_service.py
import logging
from datetime import date
from typing import Dict, List

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


# -------------------------------------------------
# STEP-1 STRUCTURAL DATA FROM NIFTY DB
# -------------------------------------------------

def get_step1_structural_data(
    nifty_db: Session,
    trade_date: date,
) -> Dict:
    """
    Fetches structural market data required for STEP-1 preview.

    Logic:
    - Identify last 6 trading days before trade_date
    - Aggregate 5-min candles into daily OHLC
    - Return yesterday + day2 + last 5 daily ranges
    """

    logger.debug(
        "[NIFTY][STEP1] Aggregation requested for trade_date=%s",
        trade_date,
    )

    # -------------------------------------------------
    # 1️⃣ Identify last 6 trading dates
    # -------------------------------------------------

    trading_days_query = text(
        """
        SELECT DISTINCT DATE(`Date`) AS trading_day
        FROM nifty_prices
        WHERE DATE(`Date`) < :trade_date
        ORDER BY trading_day DESC
        LIMIT 6
        """
    )

    result = nifty_db.execute(
        trading_days_query,
        {"trade_date": trade_date},
    )

    trading_days = [row.trading_day for row in result.fetchall()]

    if len(trading_days) < 6:
        logger.error(
            "[NIFTY][STEP1] Insufficient historical data before %s",
            trade_date,
        )
        raise ValueError("Not enough historical data for STEP-1")

    logger.debug(
        "[NIFTY][STEP1] Identified trading_days=%s",
        trading_days,
    )

    # -------------------------------------------------
    # 2️⃣ Aggregate per-day OHLC
    # -------------------------------------------------

    daily_data = {}

    for day in trading_days:
        daily_query = text(
            """
            SELECT
                MAX(`High`) AS day_high,
                MIN(`Low`) AS day_low,
                (
                    SELECT `Close`
                    FROM nifty_prices
                    WHERE DATE(`Date`) = :day
                    ORDER BY `Date` DESC
                    LIMIT 1
                ) AS day_close
            FROM nifty_prices
            WHERE DATE(`Date`) = :day
            """
        )

        row = nifty_db.execute(daily_query, {"day": day}).fetchone()

        daily_data[day] = {
            "high": float(row.day_high),
            "low": float(row.day_low),
            "close": float(row.day_close),
            "range": float(row.day_high - row.day_low),
        }

    # -------------------------------------------------
    # 3️⃣ Map to STEP-1 structure
    # -------------------------------------------------

    # trading_days is DESC ordered
    yesterday = trading_days[0]
    day2 = trading_days[1]
    last_5_days = trading_days[:5]

    structural_data = {
        "yesterday_close": daily_data[yesterday]["close"],
        "yesterday_high": daily_data[yesterday]["high"],
        "yesterday_low": daily_data[yesterday]["low"],
        "day2_high": daily_data[day2]["high"],
        "day2_low": daily_data[day2]["low"],
        "last_5_day_ranges": [
            daily_data[d]["range"] for d in last_5_days
        ],
    }

    logger.debug(
        "[NIFTY][STEP1] Aggregation complete for trade_date=%s",
        trade_date,
    )

    return structural_data