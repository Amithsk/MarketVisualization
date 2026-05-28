# backend/services/event_detection/event_validation.py

from typing import List

from constants.event_types import EventType
from models.market_event import MarketEvent


MIN_EVENT_STRENGTH_SCORE = 60

MIN_EVENT_GAP = 2


def validate_market_events(
    events: List[MarketEvent],
) -> List[MarketEvent]:

    validated_events: List[MarketEvent] = []

    last_event_index_by_type = {}

    sorted_events = sorted(
        events,
        key=lambda event: event.candle_index
    )

    for event in sorted_events:

        if (
            event.strength_score
            < MIN_EVENT_STRENGTH_SCORE
        ):
            continue

        previous_event_index = (
            last_event_index_by_type.get(
                event.event_type
            )
        )

        if (
            previous_event_index is not None
            and
            (
                event.candle_index
                - previous_event_index
            )
            < MIN_EVENT_GAP
        ):
            continue

        if not is_event_context_valid(event):
            continue

        validated_events.append(event)

        last_event_index_by_type[
            event.event_type
        ] = event.candle_index

    return validated_events


def is_event_context_valid(
    event: MarketEvent,
) -> bool:

    if (
        event.event_type
        == EventType.BREAKOUT
    ):

        if not event.validation.above_vwap:
            return False

    if (
        event.event_type
        == EventType.ORB_BREAKOUT
    ):

        if not event.validation.orb_valid:
            return False

    if (
        event.event_type
        == EventType.MOMENTUM_CONTINUATION
    ):

        if not event.validation.above_vwap:
            return False

    if (
        event.event_type
        == EventType.PULLBACK_CONTINUATION
    ):

        if not event.validation.above_vwap:
            return False

    return True