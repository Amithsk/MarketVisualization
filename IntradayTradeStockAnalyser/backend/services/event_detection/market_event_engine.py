# /IntradayTradeStockAnalyser/backend/services/event_detection/market_event_engine.py

from typing import List

from models.market_event import MarketEvent

from services.event_detection.breakout_detector import (
    detect_breakout_events,
)

from services.event_detection.event_normalization import (
    normalize_market_events,
)

from services.event_detection.event_scoring import (
    calculate_event_score,
)

from services.event_detection.event_validation import (
    validate_market_events,
)

from services.event_detection.momentum_continuation_detector import (
    detect_momentum_continuation_events,
)

from services.event_detection.orb_detector import (
    detect_orb_events,
)

from services.event_detection.pullback_continuation_detector import (
    detect_pullback_continuation_events,
)

from services.event_detection.relative_strength_detector import (
    detect_relative_strength_events,
)

from services.event_detection.volume_expansion_detector import (
    detect_volume_expansion_events,
)

from services.event_detection.vwap_event_detector import (
    detect_vwap_events,
)


def generate_market_events(
    stock_candles: List,
    nifty_candles: List,
    symbol: str,
) -> List[MarketEvent]:

    all_events: List[
        MarketEvent
    ] = []

    # -----------------------------------
    # Foundational Intelligence Layers
    # -----------------------------------

    volume_events = (
        detect_volume_expansion_events(
            candles=stock_candles,
            symbol=symbol,
        )
    )

    relative_strength_events = (
        detect_relative_strength_events(
            stock_candles=stock_candles,
            nifty_candles=nifty_candles,
            symbol=symbol,
        )
    )

    vwap_events = detect_vwap_events(
        candles=stock_candles,
        symbol=symbol,
    )

    # -----------------------------------
    # Contextual Structure Engines
    # -----------------------------------

    breakout_events = (
        detect_breakout_events(
            candles=stock_candles,
            symbol=symbol,
            volume_events=volume_events,
            relative_strength_events=(
                relative_strength_events
            ),
        )
    )

    orb_events = detect_orb_events(
        candles=stock_candles,
        symbol=symbol,
        breakout_events=breakout_events,
    )

    momentum_events = (
        detect_momentum_continuation_events(
            candles=stock_candles,
            symbol=symbol,
            breakout_events=breakout_events,
            volume_events=volume_events,
        )
    )

    pullback_events = (
        detect_pullback_continuation_events(
            candles=stock_candles,
            symbol=symbol,
            breakout_events=breakout_events,
        )
    )

    # -----------------------------------
    # Combine All Events
    # -----------------------------------

    all_events.extend(volume_events)

    all_events.extend(
        relative_strength_events
    )

    all_events.extend(vwap_events)

    all_events.extend(
        breakout_events
    )

    all_events.extend(orb_events)

    all_events.extend(
        momentum_events
    )

    all_events.extend(
        pullback_events
    )

    # -----------------------------------
    # Validation Layer
    # -----------------------------------

    validated_events = (
        validate_market_events(
            all_events
        )
    )

    # -----------------------------------
    # Centralized Scoring
    # -----------------------------------

    for event in validated_events:

        event.strength_score = (
            calculate_event_score(
                event
            )
        )

    # -----------------------------------
    # Normalization Layer
    # -----------------------------------

    normalized_events = (
        normalize_market_events(
            validated_events
        )
    )

    # -----------------------------------
    # Final Event Ordering
    # -----------------------------------

    normalized_events.sort(
        key=lambda event: (
            event.candle_index,
            -event.strength_score,
        )
    )

    return normalized_events