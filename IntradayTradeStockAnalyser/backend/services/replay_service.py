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

from backend.utils.debug_logger import (
    log_count,
    log_info,
    log_object,
    log_step,
    log_error,
)

from backend.services.market_event_service import (
    MarketEventService
)


class ReplayService:

    @staticmethod
    def get_replay_data(
        db: Session,
        trade_date: str,
        stock: str
    ):

        try:

            log_step(
                "FETCHING REPLAY DATA"
            )

            log_info(
                "Trade Date",
                trade_date
            )

            log_info(
                "Stock",
                stock
            )

            trade_data = (
                ReplayRepository
                .get_trade_metadata(
                    db,
                    trade_date,
                    stock
                )
            )

            log_object(
                "Trade Metadata",
                trade_data
            )

            nifty_candles = (
                NiftyService
                .get_nifty_candles(
                    db,
                    trade_date
                )
            )

            log_count(
                "NIFTY Candles",
                nifty_candles
            )

            if nifty_candles:

                log_object(
                    "First NIFTY Candle",
                    vars(nifty_candles[0])
                )

            stock_candles = (
                ReplayStore
                .get_stock_candles()
            )

            log_count(
                "ReplayStore Stock Candles",
                stock_candles
            )

            if stock_candles:

                log_object(
                    "First ReplayStore Candle",
                    vars(stock_candles[0])
                )

            stock_candles = [

                candle.to_dict()

                for candle in stock_candles
            ]

            log_count(
                "Serialized Stock Candles",
                stock_candles
            )

            if stock_candles:

                log_object(
                    "First Serialized Stock Candle",
                    stock_candles[0]
                )

            # =========================================
            # MARKET EVENT GENERATION
            # =========================================

            log_step(
                "GENERATING MARKET EVENTS"
            )

            market_events = (
                MarketEventService
                .generate_and_store_market_events(
                    db=db,
                    symbol=stock,
                    trade_date=trade_date,
                )
            )

            log_count(
                "Generated Market Events",
                market_events
            )

            if market_events:

                log_object(
                    "First Market Event",
                    vars(market_events[0])
                )

            serialized_market_events = [

                {

                    "id": event.id,

                    "stock_symbol": event.symbol,

                    "event_type": (
                        event.event_type.value
                    ),

                    "time": str(
                        event.timestamp
                    ),

                    "candle_index": (
                        event.candle_index
                    ),

                    "price": event.price,

                    "strength_score": (
                        event.strength_score
                    ),

                    "explanation": (
                        event.explanation
                    ),

                    "trading_implication": (
                        event.trading_implication
                    ),

                    "event_metadata": (
                        event.event_metadata
                    ),

                    "validation": vars(
                        event.validation
                    ),

                    "nifty_context": vars(
                        event.nifty_context
                    ),
                }

                for event in market_events
            ]

            log_count(
                "Serialized Market Events",
                serialized_market_events
            )

            if serialized_market_events:

                log_object(
                    "First Serialized Market Event",
                    serialized_market_events[0]
                )

            # =========================================
            # MARKET CONTEXT
            # =========================================

            market_context = (
                ReplayRepository
                .get_market_context(
                    db,
                    trade_date
                )
            )

            log_object(
                "Market Context",
                market_context
            )

            market_behavior = (
                ReplayRepository
                .get_market_behavior(
                    db,
                    trade_date
                )
            )

            log_object(
                "Market Behavior",
                market_behavior
            )

            market_open_behavior = (
                ReplayRepository
                .get_market_open_behavior(
                    db,
                    trade_date
                )
            )

            log_object(
                "Market Open Behavior",
                market_open_behavior
            )

            execution_control = (
                ReplayRepository
                .get_execution_control(
                    db,
                    trade_date
                )
            )

            log_object(
                "Execution Control",
                execution_control
            )

            stock_selection_context = (
                ReplayRepository
                .get_stock_selection_context(
                    db,
                    trade_date,
                    stock
                )
            )

            log_object(
                "Stock Selection Context",
                stock_selection_context
            )

            trade_construction = (
                ReplayRepository
                .get_trade_construction(
                    db,
                    trade_date,
                    stock
                )
            )

            log_object(
                "Trade Construction",
                trade_construction
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

            log_object(
                "Narrative Context",
                narrative_context
            )

            replay_payload = {

                "trade_data": trade_data,

                "stock_candles": stock_candles,

                "nifty_candles": [

                    {
                        **vars(candle),

                        "time": (
                            candle.time.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            if candle.time
                            else None
                        )
                    }

                    for candle in nifty_candles
                ],

                # =====================================
                # MARKET EVENTS
                # =====================================

                "market_events": (
                    serialized_market_events
                ),

                "market_context": market_context,

                "market_behavior": market_behavior,

                "market_open_behavior": market_open_behavior,

                "execution_control": execution_control,

                "stock_selection_context": stock_selection_context,

                "trade_construction": trade_construction,

                "narrative_context": narrative_context

            }

            log_step(
                "REPLAY PAYLOAD GENERATED"
            )

            log_info(
                "Replay Payload Keys",
                list(replay_payload.keys())
            )

            log_count(
                "Replay Payload Stock Candles",
                replay_payload["stock_candles"]
            )

            log_count(
                "Replay Payload NIFTY Candles",
                replay_payload["nifty_candles"]
            )

            log_count(
                "Replay Payload Market Events",
                replay_payload["market_events"]
            )

            return replay_payload

        except Exception as error:

            log_step(
                "REPLAY API FAILED"
            )

            log_error(error)

            raise