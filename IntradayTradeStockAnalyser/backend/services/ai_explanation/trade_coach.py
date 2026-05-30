# /IntradayTradeStockAnalyser/backend/services/ai_explanation/trade_coach.py

from typing import Dict, Any, List


def build_trade_coaching(
    replay_payload: Dict[str, Any]
) -> Dict[str, Any]:

    market_context = replay_payload.get(
        "market_context",
        {}
    )

    execution_control = replay_payload.get(
        "execution_control",
        {}
    )

    trade_construction = replay_payload.get(
        "trade_construction",
        {}
    )

    market_events = replay_payload.get(
        "market_events",
        []
    )

    execution_quality = _determine_execution_quality(
        market_events
    )

    entry_review = _generate_entry_review(
        market_events
    )

    stop_review = _generate_stop_review(
        market_events
    )

    exit_review = _generate_exit_review(
        market_events
    )

    strategy_review = _generate_strategy_review(
        execution_control,
        market_context
    )

    mistakes_detected = _detect_execution_mistakes(
        market_events
    )

    improvement_suggestions = (
        _generate_improvement_suggestions(
            market_events
        )
    )

    confidence_score = _calculate_confidence_score(
        market_events
    )

    return {
        "execution_quality":
            execution_quality,

        "entry_review":
            entry_review,

        "stop_review":
            stop_review,

        "exit_review":
            exit_review,

        "strategy_review":
            strategy_review,

        "mistakes_detected":
            mistakes_detected,

        "improvement_suggestions":
            improvement_suggestions,

        "confidence_score":
            confidence_score,
    }


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _determine_execution_quality(
    market_events: List[Dict[str, Any]]
) -> str:

    score = _calculate_confidence_score(
        market_events
    )

    if score >= 80:
        return "HIGH"

    if score >= 60:
        return "MODERATE"

    return "LOW"


def _generate_entry_review(
    market_events: List[Dict[str, Any]]
) -> str:

    breakout_events = [
        event
        for event in market_events
        if event.get("event_type") == "BREAKOUT"
    ]

    if breakout_events:
        return (
            "Entry aligned with bullish "
            "breakout structure."
        )

    vwap_events = [
        event
        for event in market_events
        if event.get("above_vwap")
    ]

    if vwap_events:
        return (
            "Entry remained supported "
            "above VWAP."
        )

    return (
        "Entry confirmation remained limited."
    )


def _generate_stop_review(
    market_events: List[Dict[str, Any]]
) -> str:

    vwap_support = [
        event
        for event in market_events
        if event.get("event_type") == "VWAP_HOLD"
    ]

    if vwap_support:
        return (
            "VWAP support provided logical "
            "stop structure."
        )

    return (
        "Stop placement required stronger "
        "market structure confirmation."
    )


def _generate_exit_review(
    market_events: List[Dict[str, Any]]
) -> str:

    momentum_events = [
        event
        for event in market_events
        if event.get("event_type")
        in ["BREAKOUT", "VWAP_HOLD"]
    ]

    if momentum_events:
        return (
            "Momentum continuation remained "
            "favorable after entry."
        )

    return (
        "Momentum continuation weakened "
        "during trade progression."
    )


def _generate_strategy_review(
    execution_control: Dict[str, Any],
    market_context: Dict[str, Any]
) -> str:

    strategy_name = (
        execution_control.get("strategy_name")
        or "Momentum Breakout"
    )

    market_bias = (
        market_context.get("market_bias")
        or "NEUTRAL"
    )

    if (
        strategy_name == "Momentum Breakout"
        and market_bias == "BULLISH"
    ):
        return (
            "Momentum breakout strategy aligned "
            "well with market conditions."
        )

    if market_bias == "BEARISH":
        return (
            "Strategy faced weaker market support."
        )

    return (
        "Strategy alignment remained moderate."
    )


def _detect_execution_mistakes(
    market_events: List[Dict[str, Any]]
) -> List[str]:

    mistakes = []

    weak_volume_events = [
        event
        for event in market_events
        if not event.get("volume_expansion")
    ]

    if weak_volume_events:
        mistakes.append(
            "Volume follow-through weakened "
            "during setup."
        )

    weak_rs_events = [
        event
        for event in market_events
        if event.get(
            "relative_strength_score",
            50
        ) <= 30
    ]

    if weak_rs_events:
        mistakes.append(
            "Relative strength weakened "
            "during session."
        )

    return mistakes


def _generate_improvement_suggestions(
    market_events: List[Dict[str, Any]]
) -> List[str]:

    suggestions = [
        "Avoid chasing extended breakout candles.",
        "Wait for stronger confirmation signals.",
    ]

    weak_volume_events = [
        event
        for event in market_events
        if not event.get("volume_expansion")
    ]

    if weak_volume_events:

        suggestions.append(
            "Prefer setups with stronger "
            "volume participation."
        )

    return suggestions


def _calculate_confidence_score(
    market_events: List[Dict[str, Any]]
) -> int:

    score = 0

    for event in market_events:

        if event.get("nifty_direction") == "BULLISH":
            score += 20

        if event.get("above_vwap"):
            score += 20

        if event.get("volume_expansion"):
            score += 20

        if (
            event.get(
                "relative_strength_score",
                0
            ) >= 70
        ):
            score += 20

        if event.get("orb_valid"):
            score += 20

    return min(score, 100)