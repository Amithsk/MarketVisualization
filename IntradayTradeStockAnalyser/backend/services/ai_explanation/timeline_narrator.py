# /IntradayTradeStockAnalyser/backend/services/ai_explanation/timeline_narrator.py

from typing import Dict, Any, List


IMPORTANT_EVENTS = {
    "BREAKOUT",
    "BREAKDOWN",
    "REJECTION",
    "VWAP_HOLD",
    "VWAP_REJECTION",
    "ORB_BREAKOUT",
}


def build_timeline_narration(
    replay_payload: Dict[str, Any]
) -> List[Dict[str, Any]]:

    market_events = replay_payload.get(
        "market_events",
        []
    )

    timeline_entries = []

    sorted_events = sorted(
        market_events,
        key=lambda x: x.get("candle_index", 0)
    )

    for event in sorted_events:

        event_type = event.get("event_type")

        if event_type not in IMPORTANT_EVENTS:
            continue

        timeline_entry = {
            "candle_index":
                event.get("candle_index"),

            "timestamp":
                _format_timestamp(event),

            "title":
                _generate_title(event),

            "nifty_behavior":
                _generate_nifty_behavior(event),

            "stock_behavior":
                _generate_stock_behavior(event),

            "relationship":
                _generate_relationship(event),

            "interpretation":
                _generate_interpretation(event),

            "trading_implication":
                _generate_trading_implication(event),
        }

        timeline_entries.append(
            timeline_entry
        )

    return timeline_entries


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _format_timestamp(
    event: Dict[str, Any]
) -> str:

    candle_time = event.get("candle_time")

    if not candle_time:
        return ""

    return str(candle_time)[11:16]


def _generate_title(
    event: Dict[str, Any]
) -> str:

    event_type = event.get("event_type")

    title_map = {
        "BREAKOUT":
            "Bullish Breakout Phase",

        "BREAKDOWN":
            "Breakdown Phase",

        "REJECTION":
            "Resistance Rejection",

        "VWAP_HOLD":
            "VWAP Support Confirmation",

        "VWAP_REJECTION":
            "VWAP Weakness Phase",

        "ORB_BREAKOUT":
            "Opening Range Breakout",
    }

    return title_map.get(
        event_type,
        "Market Structure Shift"
    )


def _generate_nifty_behavior(
    event: Dict[str, Any]
) -> str:

    direction = event.get("nifty_direction")

    if direction == "BULLISH":
        return (
            "NIFTY remained bullish with "
            "supportive momentum."
        )

    if direction == "BEARISH":
        return (
            "NIFTY showed weakness and "
            "broader market pressure."
        )

    return (
        "NIFTY participation remained mixed."
    )


def _generate_stock_behavior(
    event: Dict[str, Any]
) -> str:

    event_type = event.get("event_type")

    if event_type == "BREAKOUT":
        return (
            "Stock broke resistance with "
            "strong participation."
        )

    if event_type == "BREAKDOWN":
        return (
            "Stock moved below support with "
            "selling pressure."
        )

    if event_type == "REJECTION":
        return (
            "Stock failed to sustain higher "
            "levels near resistance."
        )

    if event_type == "VWAP_HOLD":
        return (
            "Stock respected VWAP support "
            "during pullback."
        )

    return (
        "Stock structure continued evolving."
    )


def _generate_relationship(
    event: Dict[str, Any]
) -> str:

    rs_score = event.get(
        "relative_strength_score",
        50
    )

    nifty_direction = event.get(
        "nifty_direction"
    )

    if nifty_direction == "BULLISH":

        if rs_score >= 70:
            return (
                "Stock aligned strongly with "
                "broader market strength."
            )

        return (
            "Stock participated with "
            "market momentum."
        )

    if nifty_direction == "BEARISH":

        if rs_score >= 70:
            return (
                "Stock remained resilient despite "
                "market weakness."
            )

        return (
            "Stock weakened along with "
            "market pressure."
        )

    return (
        "Market relationship remained mixed."
    )


def _generate_interpretation(
    event: Dict[str, Any]
) -> str:

    event_type = event.get("event_type")

    if event_type == "BREAKOUT":
        return (
            "Momentum continuation probability increased."
        )

    if event_type == "BREAKDOWN":
        return (
            "Selling pressure increased below support."
        )

    if event_type == "REJECTION":
        return (
            "Supply became visible near higher levels."
        )

    if event_type == "VWAP_HOLD":
        return (
            "Institutional participation remained active."
        )

    return (
        "Market structure continued developing."
    )


def _generate_trading_implication(
    event: Dict[str, Any]
) -> str:

    event_type = event.get("event_type")

    implication_map = {
        "BREAKOUT":
            "Favorable long opportunity.",

        "BREAKDOWN":
            "Avoid aggressive long entries.",

        "REJECTION":
            "Watch for failed continuation.",

        "VWAP_HOLD":
            "Trend continuation possible.",

        "VWAP_REJECTION":
            "Weak intraday structure.",

        "ORB_BREAKOUT":
            "Opening momentum confirmed.",
    }

    return implication_map.get(
        event_type,
        "Wait for additional confirmation."
    )