# backend/services/event_detection/orb_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)

# 09:15 → 09:45 opening range
# assuming 5-minute candles for 6 candles in the opening range

ORB_CANDLE_COUNT = 6

MIN_BODY_STRENGTH = 0.6


def detect_orb_events(
    candles: List,
    symbol: str,
    breakout_events: List[MarketEvent],
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    if len(candles) <= ORB_CANDLE_COUNT:
        return detected_events

    opening_range_candles = candles[
        :ORB_CANDLE_COUNT
    ]

    orb_high = max(
        candle.high
        for candle in opening_range_candles
    )

    orb_low = min(
        candle.low
        for candle in opening_range_candles
    )

    breakout_timestamps = {
        event.time
        for event in breakout_events
        if event.event_type == EventType.BREAKOUT
    }

    for index in range(
        ORB_CANDLE_COUNT,
        len(candles),
    ):

        current_candle = candles[index]

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

        above_vwap = (
            current_candle.close
            > current_candle.vwap
        )

        below_vwap = (
            current_candle.close
            < current_candle.vwap
        )

        orb_breakout = (
            current_candle.close
            > orb_high
        )

        orb_breakdown = (
            current_candle.close
            < orb_low
        )

        event_type = None
        explanation = ""
        implication = ""

        breakout_confirmed = (
            str(current_candle.time)
            in breakout_timestamps
        )

        if orb_breakout:

            event_type = (
                EventType.ORB_BREAKOUT
            )

            explanation = (
                "Price broke above the opening "
                "range high."
            )

            if breakout_confirmed:
                explanation += (
                    " Breakout confirmation present."
                )

            implication = (
                "Bullish momentum expansion "
                "possible."
            )

        elif orb_breakdown:

            event_type = (
                EventType.ORB_BREAKDOWN
            )

            explanation = (
                "Price broke below the opening "
                "range low."
            )

            implication = (
                "Bearish momentum continuation "
                "possible."
            )

        if not event_type:
            continue

        strength_score = 50

        if breakout_confirmed:
            strength_score += 20

        if above_vwap and orb_breakout:
            strength_score += 15

        if below_vwap and orb_breakdown:
            strength_score += 15

        strength_score = min(
            strength_score,
            100,
        )

        detected_events.append(
            MarketEvent(
                id=(
                    f"{symbol}_{event_type}_"
                    f"{current_candle.time}"
                ),

                symbol=symbol,

                event_type=event_type,

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
                    direction=(
                        "BULLISH"
                        if orb_breakout
                        else "BEARISH"
                    ),

                    relative_strength_score=0,
                ),

                validation=EventValidation(
                    above_vwap=above_vwap,

                    volume_expansion=False,

                    orb_valid=True,
                ),

                explanation=explanation,

                trading_implication=implication,

                event_metadata={
                    "orb_high": round(
                        orb_high,
                        2,
                    ),

                    "orb_low": round(
                        orb_low,
                        2,
                    ),

                    "body_strength": round(
                        body_strength,
                        2,
                    ),

                    "breakout_confirmed": (
                        breakout_confirmed
                    ),
                },
            )
        )

    return detected_events