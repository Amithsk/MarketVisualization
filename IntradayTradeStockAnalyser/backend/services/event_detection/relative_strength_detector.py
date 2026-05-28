#/IntradayTradeStockAnalyser/backend/services/event_detection/relative_strength_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)


RELATIVE_STRENGTH_THRESHOLD = 1.0
RELATIVE_WEAKNESS_THRESHOLD = -1.0


def calculate_percentage_move(
    open_price: float,
    close_price: float,
) -> float:

    if open_price <= 0:
        return 0

    return (
        (close_price - open_price)
        / open_price
    ) * 100


def detect_relative_strength_events(
    stock_candles: List,
    nifty_candles: List,
    symbol: str,
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    candle_count = min(
        len(stock_candles),
        len(nifty_candles),
    )

    for index in range(candle_count):

        stock_candle = stock_candles[index]
        nifty_candle = nifty_candles[index]

        stock_move = calculate_percentage_move(
            stock_candle.open,
            stock_candle.close,
        )

        nifty_move = calculate_percentage_move(
            nifty_candle.open,
            nifty_candle.close,
        )

        relative_strength_value = (
            stock_move - nifty_move
        )

        event_type = None
        explanation = ""
        implication = ""

        if (
            relative_strength_value
            >= RELATIVE_STRENGTH_THRESHOLD
        ):

            event_type = (
                EventType.RELATIVE_STRENGTH
            )

            explanation = (
                "Stock is outperforming NIFTY "
                "during the current candle."
            )

            implication = (
                "Momentum leadership visible."
            )

        elif (
            relative_strength_value
            <= RELATIVE_WEAKNESS_THRESHOLD
        ):

            event_type = (
                EventType.RELATIVE_WEAKNESS
            )

            explanation = (
                "Stock is underperforming NIFTY "
                "during the current candle."
            )

            implication = (
                "Weak participation visible."
            )

        if not event_type:
            continue

        strength_score = min(
            abs(relative_strength_value) * 25,
            100
        )

        detected_events.append(
            MarketEvent(
                id=(
                    f"{symbol}_{event_type}_"
                    f"{stock_candle.time}"
                ),

                symbol=symbol,

                event_type=event_type,

                timestamp=str(
                    stock_candle.time
                ),

                candle_index=index,

                price=stock_candle.close,

                strength_score=round(
                    strength_score,
                    2
                ),

                nifty_context=NiftyContext(
                    direction=(
                        "BULLISH"
                        if nifty_move > 0
                        else "BEARISH"
                    ),

                    relative_strength_score=round(
                        relative_strength_value,
                        2
                    ),
                ),

                validation=EventValidation(
                    above_vwap=False,
                    volume_expansion=False,
                    orb_valid=False,
                ),

                explanation=explanation,

                trading_implication=implication,

                event_metadata={
                    "stock_move_percent": round(
                        stock_move,
                        2
                    ),

                    "nifty_move_percent": round(
                        nifty_move,
                        2
                    ),

                    "relative_strength_value": round(
                        relative_strength_value,
                        2
                    ),
                },
            )
        )

    return detected_events