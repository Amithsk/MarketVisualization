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
                P.Date AS time,
                P.Open AS open,
                P.High AS high,
                P.Low AS low,
                P.Close AS close,
                P.Volume AS volume

            FROM nifty.nifty_prices P

            WHERE DATE(P.Date) = :trade_date
            AND TIME(P.Date) >= '09:15:00'
            AND TIME(P.Date) <= '15:15:00'

            ORDER BY P.Date ASC

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

                # Keep the database value intact; None means the source value is null.
                volume=row[5],

                # nifty_prices does not provide VWAP.
                vwap=None
            )

            candles.append(candle)

        return candles
