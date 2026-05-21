#IntradayTradeStockAnalyser/backend/repositories/trade_repository.py
from sqlalchemy import text
from sqlalchemy.orm import Session


class TradeRepository:

    @staticmethod
    def get_trade_dates(db: Session):

        query = text("""

            SELECT DISTINCT plan_date

            FROM trade_plan

            ORDER BY plan_date DESC

        """)

        result = db.execute(query)

        dates = [
            str(row[0])
            for row in result.fetchall()
        ]

        return dates
    @staticmethod
    def get_traded_stocks(db: Session, trade_date: str):

        query = text("""

        SELECT DISTINCT symbol

        FROM trade_plan

        WHERE plan_date = :trade_date

        ORDER BY symbol ASC

        """)

        result = db.execute(query,{"trade_date": trade_date } )

        stocks = [
           row[0]
        for row in result.fetchall()
           ]

        return stocks