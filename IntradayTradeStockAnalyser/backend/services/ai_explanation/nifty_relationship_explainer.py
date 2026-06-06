# /IntradayTradeStockAnalyser/backend/services/ai_explanation/nifty_relationship_explainer.py

from typing import Dict, Any, List


def build_nifty_relationship_analysis(
    replay_payload: Dict[str, Any]
) -> Dict[str, Any]:

    market_events = replay_payload.get(
        "market_events",
        []
    )

    market_context = replay_payload.get(
        "market_context",
        {}
    )

    market_direction = _determine_market_direction(
        market_events,
        market_context
    )

    relative_strength_score = (
        _extract_relative_strength_score(
            market_events
        )
    )

    stock_behavior = _determine_stock_behavior(
        market_direction,
        relative_strength_score
    )

    relationship_strength = (
        _determine_relationship_strength(
            relative_strength_score
        )
    )

    market_alignment = _generate_market_alignment(
        market_direction,
        relative_strength_score
    )

    relative_strength_analysis = (
        _generate_relative_strength_analysis(
            relative_strength_score
        )
    )

    trading_implication = (
        _generate_trading_implication(
            market_direction,
            relative_strength_score
        )
    )

    confidence_score = (
        _calculate_confidence_score(
            market_direction,
            relative_strength_score,
            market_events
        )
    )

    return {
        "market_direction": market_direction,

        "stock_behavior": stock_behavior,

        "relationship_strength":
            relationship_strength,

        "market_alignment":
            market_alignment,

        "relative_strength_analysis":
            relative_strength_analysis,

        "trading_implication":
            trading_implication,

        "confidence_score":
            confidence_score,
    }


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _determine_market_direction(
    market_events: List[Dict[str, Any]],
    market_context: Dict[str, Any]
) -> str:

    bullish_count = 0
    bearish_count = 0

    for event in market_events:

        direction = event.get("nifty_direction")

        if direction == "BULLISH":
            bullish_count += 1

        elif direction == "BEARISH":
            bearish_count += 1

    if bullish_count > bearish_count:
        return "BULLISH"

    if bearish_count > bullish_count:
        return "BEARISH"

    return (
        market_context.get("market_bias")
        or "NEUTRAL"
    )


def _extract_relative_strength_score(
    market_events: List[Dict[str, Any]]
) -> int:

    if not market_events:
        return 50

    scores = [
        event.get("relative_strength_score", 50)
        for event in market_events
    ]

    return int(sum(scores) / len(scores))


def _determine_stock_behavior(
    market_direction: str,
    rs_score: int
) -> str:

    if market_direction == "BULLISH":

        if rs_score >= 70:
            return (
                "Stock participated strongly with "
                "broader market momentum."
            )

        if rs_score <= 30:
            return (
                "Stock underperformed despite "
                "supportive market conditions."
            )

    if market_direction == "BEARISH":

        if rs_score >= 70:
            return (
                "Stock remained resilient despite "
                "market weakness."
            )

        if rs_score <= 30:
            return (
                "Stock weakened along with "
                "broader market pressure."
            )

    return (
        "Stock displayed mixed participation "
        "relative to market direction."
    )


def _determine_relationship_strength(
    rs_score: int
) -> str:

    if rs_score >= 70:
        return "HIGH"

    if rs_score <= 30:
        return "LOW"

    return "MODERATE"


def _generate_market_alignment(
    market_direction: str,
    rs_score: int
) -> str:

    if market_direction == "BULLISH" and rs_score >= 70:
        return (
            "Stock aligned strongly with "
            "bullish market momentum."
        )

    if market_direction == "BEARISH" and rs_score >= 70:
        return (
            "Stock showed leadership despite "
            "broader market weakness."
        )

    if market_direction == "BULLISH" and rs_score <= 30:
        return (
            "Stock failed to participate in "
            "market strength."
        )

    return (
        "Market alignment remained mixed."
    )


def _generate_relative_strength_analysis(
    rs_score: int
) -> str:

    if rs_score >= 70:
        return (
            "Relative strength buyers remained "
            "active throughout session."
        )

    if rs_score <= 30:
        return (
            "Relative weakness visible across "
            "multiple intraday phases."
        )

    return (
        "Relative strength participation remained neutral."
    )


def _generate_trading_implication(
    market_direction: str,
    rs_score: int
) -> str:

    if market_direction == "BULLISH" and rs_score >= 70:
        return (
            "Favorable momentum continuation environment."
        )

    if market_direction == "BEARISH" and rs_score <= 30:
        return (
            "Avoid aggressive long exposure."
        )

    if market_direction == "BEARISH" and rs_score >= 70:
        return (
            "Watch for leadership and reversal setups."
        )

    return (
        "Wait for stronger directional confirmation."
    )


def _calculate_confidence_score(
    market_direction: str,
    rs_score: int,
    market_events: List[Dict[str, Any]]
) -> int:

    score = 0

    if market_direction == "BULLISH":
        score += 30

    if market_direction == "BEARISH":
        score += 20

    if rs_score >= 70:
        score += 30

    if rs_score <= 30:
        score += 20

    volume_events = [
        event
        for event in market_events
        if event.get("volume_expansion")
    ]

    if volume_events:
        score += 20

    vwap_events = [
        event
        for event in market_events
        if event.get("above_vwap")
    ]

    if vwap_events:
        score += 20

    return min(score, 100)