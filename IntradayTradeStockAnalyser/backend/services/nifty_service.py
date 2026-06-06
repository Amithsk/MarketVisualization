from sqlalchemy.orm import Session

from backend.repositories.nifty_repository import (
    NiftyRepository
)


class NiftyService:

    @staticmethod
    def get_nifty_candles(
        db: Session,
        trade_date: str
    ):

        return (
            NiftyRepository
            .get_nifty_candles(
                db,
                trade_date
            )
        )