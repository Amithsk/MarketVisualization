# /IntradayTradeStockAnalyser/backend/services/event_detection/volume_expansion_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)


MIN_VOLUME_RATIO = 1.5
ROLLING_WINDOW = 5


def detect_volume_expansion_events(
    candles: List,
    symbol: str,
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    if len(candles) <= ROLLING_WINDOW:
        return detected_events

    for index in range(ROLLING_WINDOW, len(candles)):

        current_candle = candles[index]

        previous_candles = candles[
            index - ROLLING_WINDOW:index
        ]

        average_volume = (
            sum(c.volume for c in previous_candles)
            / ROLLING_WINDOW
        )

        if average_volume <= 0:
            continue

        volume_ratio = (
            current_candle.volume / average_volume
        )

        if volume_ratio < MIN_VOLUME_RATIO:
            continue

        strength_score = min(
            round(volume_ratio * 25, 2),
            100
        )

        if volume_ratio >= 3:
            explanation = (
                "Explosive volume expansion detected. "
                "Strong institutional participation visible."
            )

        elif volume_ratio >= 2:
            explanation = (
                "Strong volume expansion detected. "
                "Momentum participation increasing."
            )

        else:
            explanation = (
                "Notable volume expansion detected."
            )

        detected_events.append(
            MarketEvent(
                id=(
                    f"{symbol}_VOLUME_EXPANSION_"
                    f"{current_candle.time}"
                ),

                symbol=symbol,

                event_type=EventType.VOLUME_EXPANSION,

                timestamp=str(current_candle.time),

                candle_index=index,

                price=current_candle.close,

                strength_score=strength_score,

                nifty_context=NiftyContext(
                    direction="NEUTRAL",
                    relative_strength_score=0,
                ),

                validation=EventValidation(
                    above_vwap=False,
                    volume_expansion=True,
                    orb_valid=False,
                ),

                explanation=explanation,

                trading_implication=(
                    "Monitor for possible breakout, "
                    "breakdown, or momentum continuation."
                ),

                event_metadata={
                    "volume_ratio": round(volume_ratio, 2),
                    "average_volume": round(
                        average_volume,
                        2
                    ),
                    "current_volume": current_candle.volume,
                },
            )
        )

    return detected_events