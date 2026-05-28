#/IntradayTradeStockAnalyser/backend/services/market_event_service.py

from sqlalchemy.orm import Session

from backend.repositories.event_repository import (
    EventRepository,
)

from backend.repositories.nifty_repository import (
    NiftyRepository,
)

from backend.services.event_detection.market_event_engine import (
    generate_market_events,
)

from backend.utils.replay_store import (
    ReplayStore,
)


class MarketEventService:

    @staticmethod
    def generate_and_store_market_events(
        db: Session,
        symbol: str,
        trade_date: str,
    ):

        # -----------------------------------
        # Replay Candles
        # -----------------------------------

        stock_candles = (
            ReplayStore.get_stock_candles()
        )

        # -----------------------------------
        # NIFTY Candles
        # -----------------------------------

        nifty_candles = (
            NiftyRepository.get_nifty_candles(
                db=db,
                trade_date=trade_date,
            )
        )

        if not stock_candles:
            return []

        if not nifty_candles:
            return []

        # -----------------------------------
        # Generate Events
        # -----------------------------------

        market_events = (
            generate_market_events(
                stock_candles=stock_candles,
                nifty_candles=nifty_candles,
                symbol=symbol,
            )
        )

        # -----------------------------------
        # Persist Events
        # -----------------------------------

        EventRepository.save_market_events(
            db=db,
            trade_date=trade_date,
            events=market_events,
        )

        return market_events
