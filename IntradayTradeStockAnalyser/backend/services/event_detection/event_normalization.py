#/IntradayTradeStockAnalyser/backend/services/event_detection/event_normalization.py

from typing import List

from models.market_event import MarketEvent


DEFAULT_EXPLANATION = (
    "Market event detected."
)

DEFAULT_TRADING_IMPLICATION = (
    "Monitor price behavior for confirmation."
)


def normalize_market_events(
    events: List[MarketEvent],
) -> List[MarketEvent]:

    normalized_events: List[
        MarketEvent
    ] = []

    for event in events:

        normalized_event = normalize_event(
            event
        )

        normalized_events.append(
            normalized_event
        )

    return normalized_events


def normalize_event(
    event: MarketEvent,
) -> MarketEvent:

    if not event.explanation:
        event.explanation = (
            DEFAULT_EXPLANATION
        )

    if not event.trading_implication:
        event.trading_implication = (
            DEFAULT_TRADING_IMPLICATION
        )

    if event.strength_score < 0:
        event.strength_score = 0

    if event.strength_score > 100:
        event.strength_score = 100

    if event.event_metadata is None:
        event.event_metadata = {}

    event.explanation = (
        event.explanation.strip()
    )

    event.trading_implication = (
        event.trading_implication.strip()
    )

    event.event_metadata[
        "display_priority"
    ] = calculate_display_priority(
        event.strength_score
    )

    event.event_metadata[
        "event_category"
    ] = (
        event.event_type.value
        .replace("_", " ")
        .title()
    )

    return event


def calculate_display_priority(
    strength_score: float,
) -> str:

    if strength_score >= 90:
        return "CRITICAL"

    if strength_score >= 80:
        return "HIGH"

    if strength_score >= 70:
        return "MEDIUM"

    return "LOW"