# /IntradayTradeStockAnalyser/backend/services/event_detection/pullback_continuation_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)


MAX_PULLBACK_DEPTH = 0.7

MIN_RECOVERY_BODY_STRENGTH = 0.6


def detect_pullback_continuation_events(
    candles: List,
    symbol: str,
    breakout_events: List[MarketEvent],
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    breakout_timestamps = {
        event.time
        for event in breakout_events
        if event.event_type == EventType.BREAKOUT
    }

    if len(candles) < 4:
        return detected_events

    for index in range(3, len(candles)):

        breakout_candle = candles[index - 3]

        pullback_candle_1 = candles[index - 2]

        pullback_candle_2 = candles[index - 1]

        recovery_candle = candles[index]

        breakout_exists = (
            str(breakout_candle.time)
            in breakout_timestamps
        )

        if not breakout_exists:
            continue

        breakout_move = (
            breakout_candle.close
            - breakout_candle.open
        )

        if breakout_move <= 0:
            continue

        pullback_low = min(
            pullback_candle_1.low,
            pullback_candle_2.low,
        )

        pullback_depth = (
            breakout_candle.close
            - pullback_low
        )

        pullback_percent = (
            pullback_depth / breakout_move
        )

        if (
            pullback_percent
            > MAX_PULLBACK_DEPTH
        ):
            continue

        pullback_above_vwap = (
            pullback_candle_1.close
            > pullback_candle_1.vwap
            and
            pullback_candle_2.close
            > pullback_candle_2.vwap
        )

        if not pullback_above_vwap:
            continue

        recovery_bullish = (
            recovery_candle.close
            > recovery_candle.open
        )

        if not recovery_bullish:
            continue

        recovery_range = (
            recovery_candle.high
            - recovery_candle.low
        )

        if recovery_range <= 0:
            continue

        recovery_body = abs(
            recovery_candle.close
            - recovery_candle.open
        )

        body_strength = (
            recovery_body / recovery_range
        )

        if (
            body_strength
            < MIN_RECOVERY_BODY_STRENGTH
        ):
            continue

        recovery_above_vwap = (
            recovery_candle.close
            > recovery_candle.vwap
        )

        if not recovery_above_vwap:
            continue

        strength_score = 65

        if pullback_percent <= 0.4:
            strength_score += 15

        if recovery_above_vwap:
            strength_score += 10

        if body_strength >= 0.75:
            strength_score += 10

        strength_score = min(
            strength_score,
            100,
        )

        explanation_parts = [
            "Healthy pullback continuation detected.",
            "Pullback remained controlled.",
            "VWAP support held during retracement.",
            "Bullish recovery candle confirmed trend resumption.",
        ]

        detected_events.append(
            MarketEvent(
                id=(
                    f"{symbol}_PULLBACK_CONTINUATION_"
                    f"{recovery_candle.time}"
                ),

                symbol=symbol,

                event_type=(
                    EventType.PULLBACK_CONTINUATION
                ),

                timestamp=str(
                    recovery_candle.time
                ),

                candle_index=index,

                price=recovery_candle.close,

                strength_score=round(
                    strength_score,
                    2,
                ),

                nifty_context=NiftyContext(
                    direction="BULLISH",
                    relative_strength_score=0,
                ),

                validation=EventValidation(
                    above_vwap=True,
                    volume_expansion=False,
                    orb_valid=False,
                ),

                explanation=(
                    " ".join(explanation_parts)
                ),

                trading_implication=(
                    "Trend continuation setup "
                    "with controlled pullback structure."
                ),

                event_metadata={
                    "pullback_percent": round(
                        pullback_percent,
                        2,
                    ),

                    "body_strength": round(
                        body_strength,
                        2,
                    ),

                    "pullback_low": round(
                        pullback_low,
                        2,
                    ),
                },
            )
        )

    return detected_events