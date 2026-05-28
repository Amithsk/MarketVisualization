# IntradayTradeStockAnalyser/backend/repositories/nifty_repository.py

from types import SimpleNamespace

from sqlalchemy import text
from sqlalchemy.orm import Session


class NiftyRepository:

    @staticmethod
    def get_nifty_candles(
        db: Session,
        trade_date: str
    ):

        query = text("""

            SELECT
                Date,
                Open,
                High,
                Low,
                Close

            FROM nifty.nifty_prices

            WHERE DATE(Date) = :trade_date
            AND TIME(Date) >= '09:15:00'
            AND TIME(Date) <= '15:15:00'

            ORDER BY Date ASC

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date
            }
        )

        rows = result.fetchall()

        candles = []

        for row in rows:

            candle = SimpleNamespace(

                time=row[0],

                open=float(row[1]),

                high=float(row[2]),

                low=float(row[3]),

                close=float(row[4]),

                # NIFTY volume unavailable
                volume=0,

                # Placeholder VWAP
                vwap=0
            )

            candles.append(candle)

        return candles