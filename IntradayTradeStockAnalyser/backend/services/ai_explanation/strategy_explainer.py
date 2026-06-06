# /IntrdayTradeStockAnalyser/backend/services/ai_explanation/strategy_explainer.py

from typing import Dict, Any, List


def build_strategy_explanations(
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

    market_events = replay_payload.get(
        "market_events",
        []
    )

    strategy_name = (
        execution_control.get("strategy_name")
        or "Momentum Breakout"
    )

    strategy_bias = (
        market_context.get("market_bias")
        or "NEUTRAL"
    )

    selection_reasons = _build_selection_reasons(
        market_events
    )

    strategy_explanation = {
        "strategy_name": strategy_name,

        "strategy_bias": strategy_bias,

        "selection_reasons": selection_reasons,

        "market_alignment":
            _generate_market_alignment(
                strategy_bias
            ),

        "execution_expectation":
            _generate_execution_expectation(
                strategy_name
            ),

        "risk_notes":
            _generate_risk_notes(
                strategy_name
            ),

        "confidence_score":
            _calculate_strategy_confidence(
                market_events
            ),
    }

    return strategy_explanation


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _build_selection_reasons(
    market_events: List[Dict[str, Any]]
) -> List[str]:

    reasons = []

    for event in market_events:

        if event.get("nifty_direction") == "BULLISH":
            reasons.append("NIFTY bullish")

        if event.get("above_vwap"):
            reasons.append("Stock above VWAP")

        if event.get("volume_expansion"):
            reasons.append(
                "Volume expansion detected"
            )

        if (
            event.get(
                "relative_strength_score",
                0
            ) >= 70
        ):
            reasons.append(
                "Relative strength positive"
            )

        if event.get("orb_valid"):
            reasons.append(
                "Opening range breakout valid"
            )

    return list(dict.fromkeys(reasons))


def _generate_market_alignment(
    strategy_bias: str
) -> str:

    if strategy_bias == "BULLISH":
        return (
            "Strategy aligned with broader "
            "market momentum."
        )

    if strategy_bias == "BEARISH":
        return (
            "Strategy aligned with broader "
            "market weakness."
        )

    return (
        "Limited market alignment detected."
    )


def _generate_execution_expectation(
    strategy_name: str
) -> str:

    if strategy_name == "Momentum Breakout":
        return (
            "Momentum continuation expected "
            "above breakout level."
        )

    if strategy_name == "VWAP Continuation":
        return (
            "Trend continuation expected "
            "near VWAP support."
        )

    if strategy_name == "ORB Breakout":
        return (
            "Opening momentum continuation expected."
        )

    return (
        "Wait for additional confirmation."
    )


def _generate_risk_notes(
    strategy_name: str
) -> List[str]:

    notes = [
        "Avoid chasing extended candles.",
        "Watch for weak volume follow-through.",
    ]

    if strategy_name == "Momentum Breakout":

        notes.append(
            "Late entries can reduce reward-to-risk."
        )

    return notes


def _calculate_strategy_confidence(
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