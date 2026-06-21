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

    stock_candles = replay_payload.get(
        "stock_candles", []
        )
    
    
    nifty_candles = replay_payload.get(
        "nifty_candles",
            []
         )
    
    market_events = replay_payload.get(
        "market_events", 
        []
        )
    
    market_context = replay_payload.get(
        "market_context", 
        {}
        )
    
    stock_selection_context = replay_payload.get(
        "stock_selection_context", 
        {}
        )
    

    events_by_candle = _group_events_by_candle(market_events)

    explanations = {}

    for candle_index, candle in enumerate(stock_candles):

        candle_events = events_by_candle.get(candle_index, [])

        if not candle_events:
            continue
    
        stock_candle = stock_candles[
        candle_index
            ]

        nifty_candle = nifty_candles[
        candle_index
            ]
   

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
            "stock_analysis":
                _build_stock_analysis(
            stock_candle
                ),
            
            "nifty_analysis":
                _build_nifty_analysis(
            nifty_candle
                ),
            
            "relationship_analysis":
                _build_relationship_analysis(
                stock_candle,
                nifty_candle
                ),

            "action":
             _build_action_analysis(
            primary_event,
            stock_candle,
            nifty_candle
              ),
        "learning":
        _build_learning_analysis(
            primary_event,
            stock_candle,
            nifty_candle
        )

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


#Calcualte stock-level analysis metrics like move %, vwap position, etc. to enrich explanations
def _build_stock_analysis(
    stock_candle: Dict[str, Any]
) -> Dict[str, Any]:

    open_price = stock_candle.get(
        "open",
        0
    )

    close_price = stock_candle.get(
        "close",
        0
    )

    vwap = stock_candle.get(
        "vwap",
        0
    )

    # ------------------------------
    # Move %
    # ------------------------------

    move_pct = 0

    if open_price:

        move_pct = round(

            (
                (close_price - open_price)
                / open_price
            ) * 100,

            2
        )

    # ------------------------------
    # VWAP Difference
    # ------------------------------

    vwap_difference = round(
        close_price - vwap,
        2
    )

    return {

        "move": {

            "formula":
                "((Close-Open)/Open)*100",

            "open":
                open_price,

            "close":
                close_price,

            "result":
                move_pct,

            "direction":
                (
                    "BULLISH"
                    if move_pct > 0
                    else "BEARISH"
                ),

            "interpretation":
                (
                    "Price closed above open."
                    if move_pct > 0
                    else
                    "Price closed below open."
                )
        },

        "vwap_position": {

            "formula":
                "Close - VWAP",

            "close":
                close_price,

            "vwap":
                vwap,

            "result":
                vwap_difference,

            "position":
                (
                    "ABOVE"
                    if vwap_difference > 0
                    else "BELOW"
                ),

            "interpretation":
                (
                    "Price closed above VWAP."
                    if vwap_difference > 0
                    else
                    "Price closed below VWAP."
                )
        }
    }

#Function to build nifty-level analysis metrics like move % to enrich explanations
def _build_nifty_analysis(
    nifty_candle: Dict[str, Any]
) -> Dict[str, Any]:

    open_price = nifty_candle.get(
        "open",
        0
    )

    close_price = nifty_candle.get(
        "close",
        0
    )

    move_pct = 0

    if open_price:

        move_pct = round(

            (
                (close_price - open_price)
                / open_price
            ) * 100,

            2
        )

    return {

        "move": {

            "formula":
                "((Close-Open)/Open)*100",

            "open":
                open_price,

            "close":
                close_price,

            "result":
                move_pct,

            "direction":
                (
                    "BULLISH"
                    if move_pct > 0
                    else "BEARISH"
                ),

            "interpretation":
                (
                    "NIFTY closed above open."
                    if move_pct > 0
                    else
                    "NIFTY closed below open."
                )
        }
    }
#Function to analyze stock vs nifty relationship metrics to enrich explanations
def _build_relationship_analysis(
    stock_candle: Dict[str, Any],
    nifty_candle: Dict[str, Any]
) -> Dict[str, Any]:

    stock_open = stock_candle["open"]
    stock_close = stock_candle["close"]

    nifty_open = nifty_candle["open"]
    nifty_close = nifty_candle["close"]

    stock_move = round(
        ((stock_close - stock_open)
         / stock_open) * 100,
        2
    )

    nifty_move = round(
        ((nifty_close - nifty_open)
         / nifty_open) * 100,
        2
    )

    stock_direction = (
        "BULLISH"
        if stock_move > 0
        else "BEARISH"
    )

    nifty_direction = (
        "BULLISH"
        if nifty_move > 0
        else "BEARISH"
    )

    relative_strength = (
        round(
            abs(stock_move) /
            max(abs(nifty_move), 0.01),
            2
        )
    )

    return {
    "market_condition":
        f"NIFTY {nifty_direction} + "
        f"STOCK {stock_direction}",

    "stock_move_pct":
        stock_move,

    "nifty_move_pct":
        nifty_move,

    "relative_strength": {
        "formula":
            "ABS(Stock Move %) / ABS(NIFTY Move %)",
             "minimum_nifty_move_used": 0.01,

        "stock_move_pct":
            stock_move,

        "nifty_move_pct":
            nifty_move,

        "calculation":
            f"{abs(stock_move)} / "
            f"{max(abs(nifty_move), 0.01)}",

        "result":
            relative_strength,

        "interpretation":
            f"Stock moved "
            f"{relative_strength}x faster than "
            f"NIFTY during this candle."
        }
    }
#Function to build action analysis metrics like entry, stop, risk reward, invalidation to enrich explanations
def _build_action_analysis(
    event: Dict[str, Any],
    stock_candle: Dict[str, Any],
    nifty_candle: Dict[str, Any]
) -> Dict[str, Any]:

    event_type = event.get(
        "event_type",
        "UNKNOWN"
    )

    reasons = []
    why_not = []

    validation = event.get(
        "validation",
        {}
    )

    nifty_context = event.get(
        "nifty_context",
        {}
    )

    # ---------------------------
    # Event Reason
    # ---------------------------

    reasons.append(
        event_type.replace("_", " ").title()
    )

    # ---------------------------
    # VWAP
    # ---------------------------

    if validation.get("above_vwap"):
        reasons.append(
            "Above VWAP"
        )
    else:
        why_not.append(
            "Below VWAP"
        )

    # ---------------------------
    # Volume
    # ---------------------------

    if validation.get(
        "volume_expansion"
    ):
        reasons.append(
            "Volume Expansion"
        )

    # ---------------------------
    # NIFTY Context
    # ---------------------------

    nifty_direction = nifty_context.get(
        "direction",
        "NEUTRAL"
    )

    if nifty_direction == "BULLISH":
        reasons.append(
            "NIFTY Supportive"
        )

    elif nifty_direction == "BEARISH":
        why_not.append(
            "NIFTY Weak"
        )

    # ---------------------------
    # Trade Bias
    # ---------------------------

    bullish_events = {
        "BREAKOUT",
        "VWAP_RECLAIM",
        "VWAP_HOLD",
        "ORB_BREAKOUT",
        "MOMENTUM_CONTINUATION"
    }

    bearish_events = {
        "BREAKDOWN",
        "REJECTION",
        "VWAP_REJECTION"
    }

    if event_type in bullish_events:

        trade_bias = "LONG"

    elif event_type in bearish_events:

        trade_bias = "SHORT"

    else:

        trade_bias = "WATCH"

    # ---------------------------
    # Confidence
    # ---------------------------

    score = event.get(
        "strength_score",
        0
    )

    if score >= 80:

        confidence = "HIGH"

    elif score >= 60:

        confidence = "MEDIUM"

    else:

        confidence = "LOW"

    # ---------------------------
    # Would Trade
    # ---------------------------

    would_trade = score >= 60

    return {

        "would_trade":
            would_trade,

        "trade_bias":
            trade_bias,

        "confidence":
            confidence,

        "reason":
            reasons,

        "why_not":
            why_not
    }

#Function to build learning analysis metrics like concept, lesson, remember based on event type and stock/nifty behavior to enrich explanations

def _build_learning_analysis(
    event: Dict[str, Any],
    stock_candle: Dict[str, Any],
    nifty_candle: Dict[str, Any]
) -> Dict[str, Any]:

    event_type = event.get(
        "event_type",
        "UNKNOWN"
    )

    # ----------------------------------
    # Calculations
    # ----------------------------------

    stock_move = round(
        (
            (
                stock_candle["close"]
                - stock_candle["open"]
            )
            / stock_candle["open"]
        ) * 100,
        2
    )

    nifty_move = round(
        (
            (
                nifty_candle["close"]
                - nifty_candle["open"]
            )
            / nifty_candle["open"]
        ) * 100,
        2
    )

    relative_strength = round(
        abs(stock_move)
        /
        max(abs(nifty_move), 0.01),
        2
    )

    vwap_distance = round(
        stock_candle["close"]
        -
        stock_candle["vwap"],
        2
    )

    # ----------------------------------
    # Defaults
    # ----------------------------------

    concept = "Market Structure"

    lesson = (
        "Important market event detected."
    )

    remember = (
        "Wait for confirmation before trading."
    )

    # ----------------------------------
    # Event Specific Learning
    # ----------------------------------

    if event_type == "BREAKOUT":

        concept = "Bullish Breakout"

        lesson = (
            f"Stock gained {stock_move}% "
            f"while NIFTY gained "
            f"{nifty_move}%. "
            f"Relative strength was "
            f"{relative_strength}x."
        )

        remember = (
            "Breakouts supported by "
            "VWAP and market strength "
            "have higher probability "
            "of continuation."
        )

    elif event_type == "BREAKDOWN":

        concept = "Bearish Breakdown"

        lesson = (
            f"Stock moved {stock_move}% "
            f"while NIFTY moved "
            f"{nifty_move}%."
        )

        remember = (
            "Avoid buying when support "
            "has clearly failed."
        )

    elif event_type == "REJECTION":

        concept = "Resistance Rejection"

        lesson = (
            f"Price rejected higher levels "
            f"while trading "
            f"{vwap_distance} away from VWAP."
        )

        remember = (
            "Repeated rejection often "
            "signals weakness."
        )

    elif event_type == "VWAP_HOLD":

        concept = "VWAP Support"

        lesson = (
            f"Price closed "
            f"{vwap_distance} above VWAP."
        )

        remember = (
            "Strong stocks usually hold "
            "VWAP during intraday trends."
        )

    elif event_type == "VWAP_REJECTION":

        concept = "VWAP Rejection"

        lesson = (
            f"Price closed "
            f"{abs(vwap_distance)} below VWAP."
        )

        remember = (
            "Repeated VWAP rejection often "
            "indicates intraday weakness."
        )

    return {

        "concept":
            concept,

        "evidence": {

            "stock_move_pct":
                stock_move,

            "nifty_move_pct":
                nifty_move,

            "relative_strength":
                relative_strength,

            "vwap_distance":
                vwap_distance
        },

        "lesson":
            lesson,

        "remember":
            remember
    }