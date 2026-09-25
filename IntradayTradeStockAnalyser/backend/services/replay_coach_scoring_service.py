"""Deterministic Replay Coach decision-quality scoring.

This module deliberately has no provider dependency: a saved canonical coach
response can be presented and scored again without an OpenAI request.
"""
from typing import Any


class ReplayCoachScoringService:
    SCORE_VERSION = "replay_coach_score_v1"
    MAXIMUM_SCORE = 10
    RELATIVE_VOLUME_STRONG = 1.2
    RELATIVE_VOLUME_PARTIAL = 0.8
    REWARD_RISK_STRONG = 4.0
    REWARD_RISK_PARTIAL = 2.0

    @classmethod
    def score(cls, context: dict[str, Any]) -> dict[str, Any]:
        facts = context.get("decision_context", {})
        plan = context.get("documented_plan", {})
        side = (plan.get("position_type") or "").upper()
        stock, nifty = facts.get("stock_direction", {}), facts.get("nifty_direction", {})
        volume, economics = facts.get("stock_relative_volume", {}), facts.get("risk_economics", {})
        timing = facts.get("decision_timing", {})
        graph_time = cls._clock(timing.get("last_completed_stock_candle_time"))
        structure = cls._structure_component(side, facts.get("support_resistance", []), economics, graph_time)
        components = [
            cls._stock_component(side, stock, graph_time),
            cls._nifty_component(side, nifty, graph_time),
            cls._volume_component(volume, graph_time),
            structure,
            cls._rr_component(economics, structure["score"] == 2, graph_time),
        ]
        overall = sum(item["score"] for item in components)
        focus = cls._next_focus(components)
        return {
            "score_version": cls.SCORE_VERSION,
            "overall_score": overall,
            "maximum_score": cls.MAXIMUM_SCORE,
            "summary": cls._summary(components),
            "components": components,
            "next_trade_focus": focus,
        }

    @staticmethod
    def _clock(value: Any) -> str | None:
        return str(value)[11:16] if isinstance(value, str) and len(value) >= 16 else None

    @staticmethod
    def _component(component, label, score, observed, baseline, calculation, explanation, improvement, graph_time):
        return {"component": component, "label": label, "score": score, "maximum_score": 2,
                "status": "CONFIRMED" if score == 2 else "PARTIAL" if score == 1 else "NOT_ESTABLISHED",
                "observed_value": observed, "baseline": baseline, "calculation": calculation,
                "beginner_explanation": explanation, "improvement_condition": improvement,
                "graph_times": [graph_time] if graph_time else []}

    @classmethod
    def _stock_component(cls, side, stock, time):
        direction = stock.get("classification", "UNAVAILABLE")
        close, vwap = stock.get("last_completed_close"), stock.get("vwap")
        distance, pct = stock.get("distance_from_vwap_points"), stock.get("distance_from_vwap_pct")
        supports_direction = (side == "LONG" and direction == "BULLISH") or (side == "SHORT" and direction == "BEARISH")
        supports_vwap = (side == "LONG" and isinstance(distance, (int, float)) and distance > 0) or (side == "SHORT" and isinstance(distance, (int, float)) and distance < 0)
        score = 2 if supports_direction and supports_vwap else 1 if supports_direction or supports_vwap or direction == "NEUTRAL" else 0
        observed = f"Completed close {cls._price(close)}"
        baseline = f"VWAP {cls._price(vwap)}"
        calculation = "VWAP was unavailable." if distance is None else f"{cls._price(close)} − {cls._price(vwap)} = {distance:+.2f} points ({pct:+.2f}%)."
        meaning = "supported" if score == 2 else "partly supported" if score == 1 else "opposed"
        return cls._component("STOCK_DIRECTION", "Stock direction and VWAP", score, observed, baseline, calculation,
            f"The completed stock direction was {direction.lower()} and {meaning} this {side or 'trade'} idea.",
            f"For stronger {side or 'trade'} confirmation, wait for a completed candle to align with VWAP.", time)

    @classmethod
    def _nifty_component(cls, side, nifty, time):
        direction = nifty.get("classification", "UNAVAILABLE")
        score = 2 if (side == "LONG" and direction == "BULLISH") or (side == "SHORT" and direction == "BEARISH") else 1 if direction == "NEUTRAL" else 0
        return cls._component("NIFTY_ALIGNMENT", "NIFTY direction alignment", score, f"NIFTY was {direction.lower()}", "Completed NIFTY candles", "Direction uses completed candles before entry.",
            f"NIFTY {('supported' if score == 2 else 'was neutral for' if score == 1 else 'did not support')} this {side or 'trade'} idea.",
            f"Wait for NIFTY to show completed-candle {'bullish' if side == 'LONG' else 'bearish'} direction.", time)

    @classmethod
    def _volume_component(cls, volume, time):
        ratio = volume.get("ratio_vs_5_candle_median"); current = volume.get("last_completed_volume"); base = volume.get("previous_5_candle_median")
        score = 2 if isinstance(ratio, (int, float)) and ratio >= cls.RELATIVE_VOLUME_STRONG else 1 if isinstance(ratio, (int, float)) and ratio >= cls.RELATIVE_VOLUME_PARTIAL else 0
        calculation = "Baseline unavailable." if ratio is None or current is None or base is None else f"{current:,.0f} ÷ {base:,.0f} = {ratio:.2f}× ({(ratio - 1) * 100:+.0f}% versus normal)."
        return cls._component("RELATIVE_VOLUME", "Stock relative-volume confirmation", score, f"Completed volume {current:,.0f}" if current is not None else "Volume unavailable", f"Previous five-candle median {base:,.0f}" if base is not None else "Baseline unavailable", calculation,
            "Volume measures participation; it does not itself prove direction.", f"Look for at least {cls.RELATIVE_VOLUME_STRONG:.1f}× the stock's own five-candle median.", time)

    @classmethod
    def _structure_component(cls, side, levels, economics, time):
        stop = economics.get("stop"); kind = "SUPPORT" if side == "LONG" else "RESISTANCE"
        candidates = [level for level in levels if level.get("level_type") == kind and level.get("established_before_entry") and level.get("touch_count", 0) >= 2]
        level = candidates[0] if candidates else None
        valid = bool(level and stop is not None and ((side == "LONG" and float(stop) <= float(level["level"])) or (side == "SHORT" and float(stop) >= float(level["level"]))))
        score = 2 if valid else 1 if level else 0
        return cls._component("PRICE_STRUCTURE", "Price structure and structural stop", score,
            f"{kind.title()} {cls._price(level.get('level'))}" if level else "No established level", "At least two pre-entry touches and a structural stop",
            f"Touch count: {level.get('touch_count')}" if level else "Not established from available pre-entry evidence.",
            "The stop is tied to price structure." if valid else "A calculated stop alone is not evidence that the trade idea is wrong.",
            "Identify a confirmed price level first, then place the stop beyond that level.", time)

    @classmethod
    def _rr_component(cls, economics, structurally_valid, time):
        ratio, risk, reward = economics.get("reward_risk_ratio"), economics.get("risk"), economics.get("reward")
        score = 2 if structurally_valid and isinstance(ratio, (int, float)) and ratio >= cls.REWARD_RISK_STRONG else 1 if structurally_valid and isinstance(ratio, (int, float)) and ratio >= cls.REWARD_RISK_PARTIAL else 0
        calc = "Unavailable" if ratio is None else f"Reward {cls._price(reward)} ÷ risk {cls._price(risk)} = {ratio:.2f}:1."
        return cls._component("REWARD_RISK", "Reward-to-risk validity", score, f"Reward-to-risk {ratio:.2f}:1" if isinstance(ratio, (int, float)) else "Reward-to-risk unavailable", f"Required {cls.REWARD_RISK_STRONG:.0f}:1 with a structural stop", calc,
            "The ratio counts only when the stop is supported by pre-entry structure.", "Use a structural stop and keep at least ₹4 reward for every ₹1 risked.", time)

    @staticmethod
    def _price(value): return "unavailable" if value is None else f"₹{float(value):,.2f}"

    @classmethod
    def _summary(cls, components):
        good = [item["label"] for item in components if item["score"] == 2]
        weak = [item["label"] for item in components if item["score"] < 2]
        return f"{', '.join(good) or 'No component'} supported the entry; improve {', '.join(weak) or 'the documented process'}."

    @classmethod
    def _next_focus(cls, components):
        priority = ["PRICE_STRUCTURE", "REWARD_RISK", "STOCK_DIRECTION", "NIFTY_ALIGNMENT", "RELATIVE_VOLUME"]
        lowest = min(item["score"] for item in components)
        selected = next(item for key in priority for item in components if item["component"] == key and item["score"] == lowest)
        return {"component": selected["component"], "current_score": selected["score"], "target_score": 2, "message": selected["improvement_condition"]}
