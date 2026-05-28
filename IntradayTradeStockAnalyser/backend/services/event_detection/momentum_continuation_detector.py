# /IntradayTradeStockAnalyser/backend/services/event_detection/momentum_continuation_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)


MAX_PULLBACK_PERCENT = 0.5

MIN_CONTINUATION_BODY_STRENGTH = 0.6


def detect_momentum_continuation_events(
    candles: List,
    symbol: str,
    breakout_events: List[MarketEvent],
    volume_events: List[MarketEvent],
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    breakout_timestamps = {
        event.time
        for event in breakout_events
        if event.event_type == EventType.BREAKOUT
    }

    volume_event_timestamps = {
        event.time
        for event in volume_events
    }

    if len(candles) < 3:
        return detected_events

    for index in range(2, len(candles)):

        breakout_candle = candles[index - 2]

        pullback_candle = candles[index - 1]

        continuation_candle = candles[index]

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

        pullback_depth = (
            breakout_candle.close
            - pullback_candle.low
        )

        pullback_percent = (
            pullback_depth / breakout_move
        )

        if (
            pullback_percent
            > MAX_PULLBACK_PERCENT
        ):
            continue

        continuation_bullish = (
            continuation_candle.close
            > continuation_candle.open
        )

        if not continuation_bullish:
            continue

        continuation_range = (
            continuation_candle.high
            - continuation_candle.low
        )

        if continuation_range <= 0:
            continue

        continuation_body = abs(
            continuation_candle.close
            - continuation_candle.open
        )

        body_strength = (
            continuation_body
            / continuation_range
        )

        if (
            body_strength
            < MIN_CONTINUATION_BODY_STRENGTH
        ):
            continue

        above_vwap = (
            continuation_candle.close
            > continuation_candle.vwap
        )

        if not above_vwap:
            continue

        has_volume_expansion = (
            str(continuation_candle.time)
            in volume_event_timestamps
        )

        strength_score = 60

        if above_vwap:
            strength_score += 15

        if has_volume_expansion:
            strength_score += 15

        if pullback_percent <= 0.3:
            strength_score += 10

        strength_score = min(
            strength_score,
            100,
        )

        explanation_parts = [
            "Momentum continuation detected.",
            "Healthy pullback structure visible.",
            "Price holding above VWAP.",
            "Bullish continuation candle confirmed.",
        ]

        if has_volume_expansion:
            explanation_parts.append(
                "Renewed volume participation visible."
            )

        detected_events.append(
            MarketEvent(
                id=(
                    f"{symbol}_MOMENTUM_CONTINUATION_"
                    f"{continuation_candle.time}"
                ),

                symbol=symbol,

                event_type=(
                    EventType.MOMENTUM_CONTINUATION
                ),

                timestamp=str(
                    continuation_candle.time
                ),

                candle_index=index,

                price=continuation_candle.close,

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

                    volume_expansion=(
                        has_volume_expansion
                    ),

                    orb_valid=False,
                ),

                explanation=(
                    " ".join(explanation_parts)
                ),

                trading_implication=(
                    "Trend continuation possible "
                    "if momentum sustains."
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

                    "volume_confirmed": (
                        has_volume_expansion
                    ),
                },
            )
        )

    return detected_events