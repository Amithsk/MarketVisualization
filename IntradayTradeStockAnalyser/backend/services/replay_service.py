from sqlalchemy.orm import Session

from backend.repositories.replay_repository import (
    ReplayRepository
)

from backend.services.nifty_service import (
    NiftyService
)

from backend.utils.replay_store import (
    ReplayStore
)


class ReplayService:

    @staticmethod
    def get_replay_data(
        db: Session,
        trade_date: str,
        stock: str
    ):

        trade_data = (
            ReplayRepository
            .get_trade_metadata(
                db,
                trade_date,
                stock
            )
        )

        nifty_candles = (
            NiftyService
            .get_nifty_candles(
                db,
                trade_date
            )
        )

        stock_candles = (
            ReplayStore
            .get_stock_candles()
        )

        return {

            "trade_data": trade_data,

            "stock_candles": stock_candles,

            "nifty_candles": nifty_candles

        }