# /IntrdayTradeStockAnalyser/backend/services/ai_explanation/candle_explainer.py

from collections import defaultdict
from typing import Dict, List, Any


BULLISH_EVENTS = {
    "BREAKOUT",
    "VWAP_HOLD",
    "ORB_BREAKOUT",
    "MOMENTUM_CONTINUATION",
}

BEARISH_EVENTS = {
    "REJECTION",
    "BREAKDOWN",
    "VWAP_REJECTION",
}

HIGH_PRIORITY_EVENTS = {
    "BREAKOUT",
    "BREAKDOWN",
    "REJECTION",
    "VWAP_HOLD",
}


def build_candle_explanations(
    replay_payload: Dict[str, Any]
) -> Dict[int, Dict[str, Any]]:
    """
    Generate candle-level explanations using
    replay payload + detected market events.

    Returns:
        {
            candle_index: {
                explanation_data
            }
        }
    """

    stock_candles = replay_payload.get("stock_candles", [])
    market_events = replay_payload.get("market_events", [])
    market_context = replay_payload.get("market_context", {})
    stock_selection_context = replay_payload.get(
        "stock_selection_context", {}
    )

    events_by_candle = _group_events_by_candle(market_events)

    explanations = {}

    for candle_index, candle in enumerate(stock_candles):

        candle_events = events_by_candle.get(candle_index, [])

        if not candle_events:
            continue

        primary_event = _select_primary_event(candle_events)

        reasons = _generate_reasons(
            candle_events,
            stock_selection_context
        )

        explanation = {
            "title": _generate_title(primary_event),
            "summary": _generate_summary(
                primary_event,
                reasons
            ),
            "reasons": reasons,
            "market_interpretation":
                _generate_market_interpretation(
                    primary_event,
                    market_context
                ),
            "trade_implication":
                _generate_trade_implication(primary_event),
            "nifty_relationship":
                _generate_nifty_relationship(primary_event),
            "confidence_score":
                _calculate_confidence_score(
                    primary_event,
                    reasons
                ),
        }

        explanations[candle_index] = explanation

    return explanations


# =========================================================
# INTERNAL HELPERS
# =========================================================


def _group_events_by_candle(
    market_events: List[Dict[str, Any]]
) -> Dict[int, List[Dict[str, Any]]]:

    grouped = defaultdict(list)

    for event in market_events:

        candle_index = event.get("candle_index")

        if candle_index is not None:
            grouped[candle_index].append(event)

    return grouped


def _select_primary_event(
    events: List[Dict[str, Any]]
) -> Dict[str, Any]:

    # Priority-based event selection

    for priority_event in HIGH_PRIORITY_EVENTS:
        for event in events:
            if event.get("event_type") == priority_event:
                return event

    return events[0]


def _generate_title(
    event: Dict[str, Any]
) -> str:

    event_type = event.get("event_type", "")

    title_map = {
        "BREAKOUT": "Bullish Breakout Candle",
        "BREAKDOWN": "Bearish Breakdown Candle",
        "REJECTION": "Rejection Candle",
        "VWAP_HOLD": "VWAP Support Confirmation",
        "VWAP_REJECTION": "VWAP Rejection Candle",
        "ORB_BREAKOUT": "Opening Range Breakout",
        "MOMENTUM_CONTINUATION": "Momentum Continuation Candle",
    }

    return title_map.get(
        event_type,
        "Market Structure Candle"
    )


def _generate_reasons(
    events: List[Dict[str, Any]],
    stock_selection_context: Dict[str, Any]
) -> List[str]:

    reasons = []

    for event in events:

        if event.get("above_vwap"):
            reasons.append("Above VWAP")

        if event.get("volume_expansion"):
            reasons.append("Volume expansion detected")

        if event.get("orb_valid"):
            reasons.append("Opening range breakout valid")

        nifty_direction = event.get("nifty_direction")

        if nifty_direction == "BULLISH":
            reasons.append("NIFTY bullish")

        elif nifty_direction == "BEARISH":
            reasons.append("NIFTY bearish")

        rs_score = event.get("relative_strength_score", 0)

        if rs_score >= 70:
            reasons.append("Relative strength positive")

        elif rs_score <= 30:
            reasons.append("Relative weakness visible")

    if stock_selection_context.get("tradable"):
        reasons.append("Stock passed selection filters")

    # Remove duplicates while preserving order
    unique_reasons = list(dict.fromkeys(reasons))

    return unique_reasons


def _generate_summary(
    event: Dict[str, Any],
    reasons: List[str]
) -> str:

    event_type = event.get("event_type", "")

    if event_type == "BREAKOUT":
        return (
            "Price broke above resistance with "
            "strong participation."
        )

    if event_type == "BREAKDOWN":
        return (
            "Price moved below support with "
            "increasing selling pressure."
        )

    if event_type == "REJECTION":
        return (
            "Price failed to sustain higher levels "
            "and faced rejection."
        )

    if event_type == "VWAP_HOLD":
        return (
            "Price respected VWAP support indicating "
            "institutional participation."
        )

    if reasons:
        return " | ".join(reasons)

    return "Important market structure candle."


def _generate_market_interpretation(
    event: Dict[str, Any],
    market_context: Dict[str, Any]
) -> str:

    event_type = event.get("event_type", "")
    market_bias = market_context.get("market_bias")

    if event_type == "BREAKOUT":

        if market_bias == "BULLISH":
            return (
                "Momentum continuation possible "
                "with favorable market alignment."
            )

        return (
            "Breakout visible but broader market "
            "confirmation limited."
        )

    if event_type == "REJECTION":
        return (
            "Selling pressure visible near resistance."
        )

    if event.get("above_vwap"):
        return (
            "Institutional support appears active "
            "above VWAP."
        )

    return "Market structure evolving."


def _generate_trade_implication(
    event: Dict[str, Any]
) -> str:

    event_type = event.get("event_type", "")

    implication_map = {
        "BREAKOUT": "Favorable long setup.",
        "BREAKDOWN": "Avoid aggressive long entries.",
        "REJECTION": "Caution near resistance.",
        "VWAP_HOLD": "Trend continuation possible.",
        "VWAP_REJECTION": "Weak intraday structure.",
        "ORB_BREAKOUT": "Opening momentum confirmed.",
    }

    return implication_map.get(
        event_type,
        "Wait for additional confirmation."
    )


def _generate_nifty_relationship(
    event: Dict[str, Any]
) -> str:

    nifty_direction = event.get("nifty_direction")
    relative_strength_score = event.get(
        "relative_strength_score",
        0
    )

    if nifty_direction == "BULLISH":

        if relative_strength_score >= 70:
            return (
                "Stock aligned strongly with "
                "broader market momentum."
            )

        return (
            "Stock participated in broader "
            "market strength."
        )

    if nifty_direction == "BEARISH":

        if relative_strength_score >= 70:
            return (
                "Stock showed resilience despite "
                "market weakness."
            )

        return (
            "Stock weakened along with market pressure."
        )

    return "Limited market correlation detected."


def _calculate_confidence_score(
    event: Dict[str, Any],
    reasons: List[str]
) -> int:

    score = 0

    event_type = event.get("event_type")

    if event_type == "BREAKOUT":
        score += 25

    if event.get("above_vwap"):
        score += 20

    if event.get("volume_expansion"):
        score += 20

    if event.get("orb_valid"):
        score += 15

    rs_score = event.get("relative_strength_score", 0)

    if rs_score >= 70:
        score += 20

    score += min(len(reasons) * 2, 10)

    return min(score, 100)

