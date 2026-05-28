#/IntradayTradeStockAnalyser/backend/services/event_detection/vwap_event_detector.py

from typing import List

from constants.event_types import EventType
from models.market_event import (
    EventValidation,
    MarketEvent,
    NiftyContext,
)


def detect_vwap_events(
    candles: List,
    symbol: str,
) -> List[MarketEvent]:

    detected_events: List[MarketEvent] = []

    if len(candles) < 2:
        return detected_events

    for index in range(1, len(candles)):

        previous_candle = candles[index - 1]
        current_candle = candles[index]

        previous_below_vwap = (
            previous_candle.close
            < previous_candle.vwap
        )

        current_above_vwap = (
            current_candle.close
            > current_candle.vwap
        )

        bullish_body = (
            current_candle.close
            > current_candle.open
        )

        reclaim_detected = (
            previous_below_vwap
            and current_above_vwap
            and bullish_body
        )

        vwap_tested = (
            current_candle.high
            >= current_candle.vwap
        )

        weak_close = (
            current_candle.close
            < current_candle.vwap
        )

        bearish_body = (
            current_candle.close
            < current_candle.open
        )

        rejection_detected = (
            vwap_tested
            and weak_close
            and bearish_body
        )

        event_type = None
        explanation = ""
        implication = ""

        if reclaim_detected:

            event_type = (
                EventType.VWAP_RECLAIM
            )

            explanation = (
                "Price reclaimed VWAP with "
                "bullish candle confirmation."
            )

            implication = (
                "Buyers may be regaining control."
            )

        elif rejection_detected:

            event_type = (
                EventType.VWAP_REJECTION
            )

            explanation = (
                "Price failed to sustain above "
                "VWAP and faced rejection."
            )

            implication = (
                "Sellers defending VWAP resistance."
            )

        if not event_type:
            continue

        candle_range = (
            current_candle.high
            - current_candle.low
        )

        candle_body = abs(
            current_candle.close
            - current_candle.open
        )

        body_strength = (
            candle_body / candle_range
            if candle_range > 0
            else 0
        )

        strength_score = min(
            round(body_strength * 100, 2),
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

                strength_score=strength_score,

                nifty_context=NiftyContext(
                    direction="NEUTRAL",
                    relative_strength_score=0,
                ),

                validation=EventValidation(
                    above_vwap=current_above_vwap,
                    volume_expansion=False,
                    orb_valid=False,
                ),

                explanation=explanation,

                trading_implication=implication,

                event_metadata={
                    "vwap": round(
                        current_candle.vwap,
                        2
                    ),

                    "body_strength": round(
                        body_strength,
                        2
                    ),
                },
            )
        )

    return detected_events