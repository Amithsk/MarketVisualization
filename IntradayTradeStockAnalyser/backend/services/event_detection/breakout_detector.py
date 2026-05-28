# /IntradayTradeStockAnalyser/backend/services/event_detection/breakout_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)


LOOKBACK_PERIOD = 5

MIN_BODY_STRENGTH = 0.6

MIN_CLOSE_NEAR_HIGH = 0.7


def detect_breakout_events(
    candles: List,
    symbol: str,
    volume_events: List[MarketEvent],
    relative_strength_events: List[MarketEvent],
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    volume_event_timestamps = {
        event.time
        for event in volume_events
    }

    relative_strength_timestamps = {
        event.time
        for event in relative_strength_events
        if (
            event.event_type
            == EventType.RELATIVE_STRENGTH
        )
    }

    if len(candles) <= LOOKBACK_PERIOD:
        return detected_events

    for index in range(
        LOOKBACK_PERIOD,
        len(candles),
    ):

        current_candle = candles[index]

        previous_candles = candles[
            index - LOOKBACK_PERIOD:index
        ]

        resistance_level = max(
            candle.high
            for candle in previous_candles
        )

        breakout_detected = (
            current_candle.close
            > resistance_level
        )

        if not breakout_detected:
            continue

        candle_range = (
            current_candle.high
            - current_candle.low
        )

        if candle_range <= 0:
            continue

        candle_body = abs(
            current_candle.close
            - current_candle.open
        )

        body_strength = (
            candle_body / candle_range
        )

        if (
            body_strength
            < MIN_BODY_STRENGTH
        ):
            continue

        close_position = (
            (
                current_candle.close
                - current_candle.low
            )
            / candle_range
        )

        if (
            close_position
            < MIN_CLOSE_NEAR_HIGH
        ):
            continue

        above_vwap = (
            current_candle.close
            > current_candle.vwap
        )

        if not above_vwap:
            continue

        has_volume_expansion = (
            str(current_candle.time)
            in volume_event_timestamps
        )

        has_relative_strength = (
            str(current_candle.time)
            in relative_strength_timestamps
        )

        strength_score = 50

        if above_vwap:
            strength_score += 20

        if has_volume_expansion:
            strength_score += 15

        if has_relative_strength:
            strength_score += 15

        strength_score = min(
            strength_score,
            100,
        )

        explanation_parts = [
            "Resistance breakout detected.",
            "Strong bullish candle structure.",
            "Price closed near candle high.",
            "Breakout occurred above VWAP.",
        ]

        if has_volume_expansion:
            explanation_parts.append(
                "Volume expansion confirmed."
            )

        if has_relative_strength:
            explanation_parts.append(
                "Stock outperforming NIFTY."
            )

        detected_events.append(
            MarketEvent(
                id=(
                    f"{symbol}_BREAKOUT_"
                    f"{current_candle.time}"
                ),

                symbol=symbol,

                event_type=EventType.BREAKOUT,

                timestamp=str(
                    current_candle.time
                ),

                candle_index=index,

                price=current_candle.close,

                strength_score=round(
                    strength_score,
                    2,
                ),

                nifty_context=NiftyContext(
                    direction="NEUTRAL",
                    relative_strength_score=(
                        1 if has_relative_strength
                        else 0
                    ),
                ),

                validation=EventValidation(
                    above_vwap=above_vwap,

                    volume_expansion=(
                        has_volume_expansion
                    ),

                    orb_valid=False,
                ),

                explanation=(
                    " ".join(explanation_parts)
                ),

                trading_implication=(
                    "Momentum continuation "
                    "possible if follow-through "
                    "buying continues."
                ),

                event_metadata={
                    "resistance_level": round(
                        resistance_level,
                        2,
                    ),

                    "body_strength": round(
                        body_strength,
                        2,
                    ),

                    "close_position": round(
                        close_position,
                        2,
                    ),

                    "volume_confirmed": (
                        has_volume_expansion
                    ),

                    "relative_strength_confirmed": (
                        has_relative_strength
                    ),
                },
            )
        )

    return detected_events