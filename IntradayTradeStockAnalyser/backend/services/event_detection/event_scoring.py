#/IntradayTradeStockAnalyser/backend/services/event_detection/event_scoring.py

from models.market_event import MarketEvent


BASE_SCORE = 50

VWAP_WEIGHT = 20

VOLUME_WEIGHT = 20

RELATIVE_STRENGTH_WEIGHT = 20

ORB_WEIGHT = 15

STRUCTURE_WEIGHT = 15

MAX_SCORE = 100


def calculate_event_score(
    event: MarketEvent,
) -> float:

    score = BASE_SCORE

    if event.validation.above_vwap:
        score += VWAP_WEIGHT

    if event.validation.volume_expansion:
        score += VOLUME_WEIGHT

    if event.validation.orb_valid:
        score += ORB_WEIGHT

    relative_strength_score = (
        abs(
            event.nifty_context
            .relative_strength_score
        )
    )

    if relative_strength_score >= 1:
        score += RELATIVE_STRENGTH_WEIGHT

    body_strength = (
        event.event_metadata.get(
            "body_strength",
            0,
        )
        if event.event_metadata
        else 0
    )

    if body_strength >= 0.7:
        score += STRUCTURE_WEIGHT

    return min(score, MAX_SCORE)