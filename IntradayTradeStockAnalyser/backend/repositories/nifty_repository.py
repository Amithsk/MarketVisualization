#IntradayTradeStockAnalyser/backend/repositories/nifty_repository.py
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

            candles.append({

                "time": row[0].strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "open": row[1],

                "high": row[2],

                "low": row[3],

                "close": row[4],

                # NIFTY volume unavailable currently
                "volume": 0

            })

        return candles