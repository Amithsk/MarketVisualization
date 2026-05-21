from sqlalchemy.orm import Session

from backend.repositories.trade_repository import (
    TradeRepository
)


class TradeService:

    @staticmethod
    def get_trade_dates(db: Session):

        return (
            TradeRepository
            .get_trade_dates(db)
            
        )
    @staticmethod
    def get_traded_stocks(db: Session,trade_date: str):
        return (
        TradeRepository
        .get_traded_stocks(
            db,
            trade_date
        )
      )