#IntradayTradeStockAnalyser/backend/services/replay_service.py

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

from backend.services.replay_narrative_service import (
    ReplayNarrativeService
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

        stock_candles = [

            candle.to_dict()

            for candle in stock_candles
        ]

        market_context = (
            ReplayRepository
            .get_market_context(
                db,
                trade_date
            )
        )

        market_behavior = (
            ReplayRepository
            .get_market_behavior(
                db,
                trade_date
            )
        )

        market_open_behavior = (
            ReplayRepository
            .get_market_open_behavior(
                db,
                trade_date
            )
        )

        execution_control = (
            ReplayRepository
            .get_execution_control(
                db,
                trade_date
            )
        )

        stock_selection_context = (
            ReplayRepository
            .get_stock_selection_context(
                db,
                trade_date,
                stock
            )
        )

        trade_construction = (
            ReplayRepository
            .get_trade_construction(
                db,
                trade_date,
                stock
            )
        )

        narrative_context = (
            ReplayNarrativeService
            .build_replay_narrative(
                market_context=market_context,
                market_behavior=market_behavior,
                market_open_behavior=market_open_behavior,
                execution_control=execution_control,
                stock_selection_context=stock_selection_context,
                trade_construction=trade_construction
            )
        )

        return {

            "trade_data": trade_data,

            "stock_candles": stock_candles,

            "nifty_candles": nifty_candles,

            "market_context": market_context,

            "market_behavior": market_behavior,

            "market_open_behavior": market_open_behavior,

            "execution_control": execution_control,

            "stock_selection_context": stock_selection_context,

            "trade_construction": trade_construction,

            "narrative_context": narrative_context

        }