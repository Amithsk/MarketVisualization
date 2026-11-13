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
        support_validity, structural_stop = cls._structure_components(side, facts.get("support_resistance", []), economics, graph_time)
        components = [
            cls._stock_component(side, facts, graph_time),
            cls._nifty_component(side, facts, graph_time),
            cls._volume_component(volume, graph_time),
            support_validity,
            structural_stop,
            cls._rr_component(economics, structural_stop["score"] == 1, graph_time),
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
    def _component(component, label, score, observed, baseline, calculation, explanation, improvement, graph_time, maximum_score=2, status=None, **evidence):
        return {"component": component, "label": label, "score": score, "maximum_score": maximum_score,
                "status": status or ("CONFIRMED" if score == maximum_score else "PARTIAL" if score else "NOT_ESTABLISHED"),
                "observed_value": observed, "baseline": baseline, "calculation": calculation,
                "beginner_explanation": explanation, "improvement_condition": improvement,
                "graph_times": evidence.pop("graph_times", [graph_time] if graph_time else []), **evidence}

    @classmethod
    def _stock_component(cls, side, facts, time):
        stock = facts.get("stock_direction", {})
        broader = facts.get("stock_session_structure", {})
        structure = broader.get("classification") or stock.get("session_structure") or stock.get("classification", "NOT_ASSESSABLE")
        recent = facts.get("stock_recent_momentum", {})
        momentum = recent.get("classification") or stock.get("classification", "NEUTRAL")
        latest = facts.get("stock_latest_completed_candle", {})
        vwap_facts = facts.get("stock_vwap_location", {})
        location = vwap_facts.get("location") or ("ABOVE" if isinstance(stock.get("distance_from_vwap_points"), (int, float)) and stock["distance_from_vwap_points"] > 0 else "BELOW" if isinstance(stock.get("distance_from_vwap_points"), (int, float)) and stock["distance_from_vwap_points"] < 0 else "UNAVAILABLE")
        close, vwap = vwap_facts.get("last_completed_close", stock.get("last_completed_close")), vwap_facts.get("vwap", stock.get("vwap"))
        supportive_latest = latest.get("classification") in (("BULLISH_PROGRESS", "RECOVERY") if side == "LONG" else ("BEARISH_PROGRESS", "PULLBACK"))
        structural = (side == "LONG" and structure == "BULLISH") or (side == "SHORT" and structure == "BEARISH")
        momentum_ok = (side == "LONG" and momentum == "BULLISH") or (side == "SHORT" and momentum == "BEARISH")
        vwap_ok = (side == "LONG" and location == "ABOVE") or (side == "SHORT" and location == "BELOW")
        conflicts = [(structure == "BEARISH" if side == "LONG" else structure == "BULLISH"), (momentum == "BEARISH" if side == "LONG" else momentum == "BULLISH"), (latest.get("classification") == ("BEARISH_PROGRESS" if side == "LONG" else "BULLISH_PROGRESS")), (location == ("BELOW" if side == "LONG" else "ABOVE"))]
        supports = [structural, momentum_ok, supportive_latest, vwap_ok]
        score = 2 if structural and (momentum_ok or supportive_latest) and vwap_ok and not any(conflicts) else 1 if any(supports) else 0
        alignment = "FULL_ALIGNMENT" if score == 2 else "PARTIAL_ALIGNMENT" if score == 1 else "NOT_ASSESSABLE" if structure == "NOT_ASSESSABLE" and not any(supports) else "NO_ALIGNMENT"
        timing = facts.get("decision_timing", {})
        graph_times = [cls._clock(item.get("time")) for item in broader.get("confirmed_swing_highs", []) + broader.get("confirmed_swing_lows", [])]
        for window in (recent.get("three_candle"), recent.get("five_candle")):
            if window: graph_times.extend([cls._clock(window["start_time"]), cls._clock(window["end_time"])])
        graph_times.extend([cls._clock(latest.get("previous_interval_start")), cls._clock(latest.get("interval_start"))])
        evidence = {"decision_boundary":{"entry_time":timing.get("entry_time"),"last_completed_candle_start":timing.get("last_completed_stock_candle_time"),"excluded_forming_candle_start":timing.get("containing_candle_start"),"excluded_forming_candle_end":timing.get("containing_candle_end"),"timestamp_semantics":"CANDLE_OPEN"},"broader_structure":broader,"recent_momentum":recent,"latest_completed_candle":latest,"vwap_location":vwap_facts,"alignment":{"classification":alignment,"supporting_factors":[name for name,ok in (("broader structure",structural),("recent momentum",momentum_ok),("latest completed candle",supportive_latest),("VWAP location",vwap_ok)) if ok],"conflicting_factors":[name for name,conflict in (("broader structure",conflicts[0]),("recent momentum",conflicts[1]),("latest completed candle",conflicts[2]),("VWAP location",conflicts[3])) if conflict],"neutral_factors":["broader structure" if structure=="UNCONFIRMED" else ""]}}
        return cls._component("STOCK_DIRECTION", "Stock direction and VWAP", score,
            f"Structure {structure.lower()}; recent momentum {momentum.lower()}; latest candle {latest.get('classification', 'not assessable').lower()}; close {cls._price(close)}",
            f"VWAP {cls._price(vwap)} ({location})", "Broader structure, momentum, latest-candle behaviour, and VWAP are separate decision-time facts.",
            f"Evidence was {'fully' if score == 2 else 'partially' if score == 1 else 'not'} aligned with the {side or 'planned'} trade. Structure was {structure.lower()} and momentum was {momentum.lower()}.", "Check confirmed swings, momentum, the latest completed candle, and VWAP together.", time, status=alignment, stock_direction_evidence=evidence, calculation_lines=[{"label":"Decision boundary","formula":"Last completed candle", "result":str(timing.get("last_completed_stock_candle_time") or "unavailable")},{"label":"Broader structure","formula":f"Swing highs {len(broader.get('confirmed_swing_highs', []))}/{broader.get('required_swing_highs', 2)}; swing lows {len(broader.get('confirmed_swing_lows', []))}/{broader.get('required_swing_lows', 2)}", "result":structure},{"label":"Latest completed candle","formula":str(latest.get("interval_start") or "unavailable"), "result":str(latest.get("classification") or "NOT_ASSESSABLE")},{"label":"VWAP distance","formula":f"{cls._price(close)} − {cls._price(vwap)}", "result":f"{vwap_facts.get('distance_from_vwap_points', stock.get('distance_from_vwap_points', 'unavailable'))} points ({location})"}], graph_times=list(dict.fromkeys(x for x in graph_times if x)))

    def _legacy_stock_component(cls, side, stock, time):
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
    def _nifty_component(cls, side, facts, time):
        nifty = facts.get("nifty_direction", {})
        direction = facts.get("nifty_session_structure", {}).get("classification") or nifty.get("session_structure") or nifty.get("classification", "UNAVAILABLE")
        score = 2 if (side == "LONG" and direction == "BULLISH") or (side == "SHORT" and direction == "BEARISH") else 1 if direction == "NEUTRAL" else 0
        return cls._component("NIFTY_ALIGNMENT", "NIFTY direction alignment", score, f"NIFTY was {direction.lower()}", "Completed NIFTY candles", "Direction uses completed candles before entry.",
            f"NIFTY {('supported' if score == 2 else 'was neutral for' if score == 1 else 'did not support')} this {side or 'trade'} idea.",
            f"Wait for NIFTY to show completed-candle {'bullish' if side == 'LONG' else 'bearish'} direction.", time)

    @classmethod
    def _volume_component(cls, volume, time):
        ratio = volume.get("ratio_vs_5_candle_median"); current = volume.get("last_completed_volume"); base = volume.get("previous_5_candle_median")
        score = 2 if isinstance(ratio, (int, float)) and ratio >= cls.RELATIVE_VOLUME_STRONG else 1 if isinstance(ratio, (int, float)) and ratio >= cls.RELATIVE_VOLUME_PARTIAL else 0
        calculation = "Baseline unavailable." if ratio is None or current is None or base is None else f"{current:,.0f} ÷ {base:,.0f} = {ratio:.2f}× ({(ratio - 1) * 100:+.0f}% versus normal)."
        assessment = "passed" if score == 2 else "was below the system scoring default" if ratio is not None else "could not be assessed"
        return cls._component("RELATIVE_VOLUME", "Stock relative-volume confirmation", score, f"Completed volume {current:,.0f}" if current is not None else "Volume unavailable", f"System scoring default: {cls.RELATIVE_VOLUME_STRONG:.1f}× the previous five-candle median" if base is not None else "Baseline unavailable", calculation,
            f"The observed volume {assessment}; volume measures participation and does not itself prove direction.", f"For the system's strongest score, use at least {cls.RELATIVE_VOLUME_STRONG:.1f}× the stock's own five-candle median.", time)

    @classmethod
    def _structure_components(cls, side, levels, economics, time):
        kind = "SUPPORT" if side == "LONG" else "RESISTANCE" if side == "SHORT" else None
        candidates = [level for level in levels if kind and level.get("level_type") == kind and level.get("established_before_entry") and level.get("touch_count", 0) >= level.get("required_reactions", 2)]
        level = candidates[0] if candidates else None
        sources = level.get("source_candles", []) if level else []
        assessable = bool(level and sources)
        active = bool(assessable and not level.get("invalidated", False))
        status = "CONFIRMED" if active else "NOT_ASSESSABLE" if level and not sources else "NOT_CONFIRMED"
        source_times = [cls._clock(item.get("time")) for item in sources]
        penetration_times = [cls._clock(item.get("time")) for item in (level.get("penetrations", []) if level else [])]
        graph_times = list(dict.fromkeys([item for item in source_times + penetration_times if item]))
        calculation_lines = cls._level_calculations(level, kind) if level else []
        validity = cls._component("SUPPORT_VALIDITY" if kind == "SUPPORT" else "RESISTANCE_VALIDITY", f"{kind.title()} validity" if kind else "Structure validity", 1 if active else 0,
            f"{kind.title()} centre {cls._price(level.get('level'))}" if level else "No established level", f"{level.get('touch_count', 0) if level else 0}/{level.get('required_reactions', 2) if level else 2} completed pre-entry reactions",
            calculation_lines[0]["formula"] + " = " + calculation_lines[0]["result"] if calculation_lines else "No reconstructable completed-candle calculation.",
            (f"{level.get('touch_count')} pre-entry reactions formed the {kind.lower()} and it remained active at entry." if active else "The available completed-candle evidence was insufficient to assess structure safely." if status == "NOT_ASSESSABLE" else f"The pre-entry structural level was not sufficiently established or had already been invalidated."),
            "First confirm that the level was active at entry. Then place the stop beyond the complete structural boundary.", time, maximum_score=1, status=status, level=cls._level_evidence(level), source_candles=sources, penetrations=level.get("penetrations", []) if level else [], calculation_lines=calculation_lines, graph_times=graph_times)
        stop = economics.get("stop"); extreme = level.get("structural_extreme") if level else None
        placement = "UNAVAILABLE"
        if active and stop is not None and extreme:
            stop = float(stop); centre, lower, upper, value = float(level["level"]), float(level["zone_lower"]), float(level["zone_upper"]), float(extreme["value"])
            beyond_extreme = stop < value if kind == "SUPPORT" else stop > value
            beyond_zone = stop < lower if kind == "SUPPORT" else stop > upper
            beyond_centre = stop < centre if kind == "SUPPORT" else stop > centre
            placement = "BEYOND_COMPLETE_STRUCTURE" if beyond_extreme else "BEYOND_ZONE_NOT_STRUCTURAL_EXTREME" if beyond_zone else "BEYOND_CENTRE_ONLY" if beyond_centre else "INSIDE_DETECTED_ZONE"
        stop_score = 1 if placement == "BEYOND_COMPLETE_STRUCTURE" else 0
        stop_status = "CONFIRMED" if stop_score else "NOT_ASSESSABLE" if not assessable or stop is None or not extreme else "NOT_CONFIRMED"
        stop_lines = cls._stop_calculations(kind, level, stop, extreme) if level and stop is not None and extreme else []
        stop_component = cls._component("STRUCTURAL_STOP", "Structural stop placement", stop_score, f"Stop {cls._price(stop)}" if stop is not None else "Stop unavailable", placement.replace("_", " ").title(),
            "; ".join(line["formula"] + " = " + line["result"] for line in stop_lines) or "Stop placement cannot be reconstructed safely.",
            "The stop was beyond the complete structural boundary." if stop_score else "The stop was below/above the calculated centre but remained inside the complete structural range." if placement == "BEYOND_CENTRE_ONLY" else "The stop could not be verified beyond the complete pre-entry structure.",
            "If a stop beyond the full structure creates excessive risk or reward:risk, skip the trade rather than forcing a wider stop.", time, maximum_score=1, status=stop_status, stop_price=stop, level_centre=level.get("level") if level else None, zone_boundary=(level.get("zone_lower") if kind == "SUPPORT" and level else level.get("zone_upper") if level else None), structural_extreme=extreme, placement=placement, calculation_lines=stop_lines, graph_times=graph_times)
        return validity, stop_component

    @classmethod
    def _level_evidence(cls, level):
        if not level: return None
        return {key: level.get(key) for key in ("level_type", "method", "level", "zone_lower", "zone_upper", "required_reactions", "touch_count", "invalidation_required_closes", "invalidation_consecutive_closes", "invalidated")}
    @classmethod
    def _level_calculations(cls, level, kind):
        if not level: return []
        values = [item["value"] for item in level.get("source_candles", [])]
        formula = " + ".join(cls._price(value) for value in values) + f" ÷ {len(values)}" if values else "Unavailable"
        return [{"label": f"{kind.title()} centre", "formula": formula, "result": cls._price(level.get("level"))}]
    @classmethod
    def _stop_calculations(cls, kind, level, stop, extreme):
        if kind == "SUPPORT": return [{"label": "Below support centre", "formula": f"{cls._price(level['level'])} − {cls._price(stop)}", "result": cls._price(float(level['level']) - stop)}, {"label": "Position relative to structural low", "formula": f"{cls._price(stop)} − {cls._price(extreme['value'])}", "result": f"{cls._price(abs(stop - float(extreme['value'])))} {'below' if stop < float(extreme['value']) else 'above'} the structural low"}]
        return [{"label": "Above resistance centre", "formula": f"{cls._price(stop)} − {cls._price(level['level'])}", "result": cls._price(stop - float(level['level']))}, {"label": "Position relative to structural high", "formula": f"{cls._price(extreme['value'])} − {cls._price(stop)}", "result": f"{cls._price(abs(float(extreme['value']) - stop))} {'above' if stop > float(extreme['value']) else 'below'} the structural high"}]

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
        validity = next((item for item in components if item["component"] in ("SUPPORT_VALIDITY", "RESISTANCE_VALIDITY")), None)
        stop = next((item for item in components if item["component"] == "STRUCTURAL_STOP"), None)
        if validity and validity["score"] == validity["maximum_score"] and stop and stop["score"] == stop["maximum_score"]:
            structural = "Pre-entry structure was valid and the stop was beyond the required structural boundary."
        elif validity and validity["score"] == validity["maximum_score"]:
            structural = f"Pre-entry {validity['label'].replace(' validity', '').lower()} was identifiable, but the stop remained inside the complete structural range."
        elif validity and validity["status"] == "NOT_ASSESSABLE":
            structural = "The available completed-candle evidence was insufficient to assess structure safely."
        else: structural = "The pre-entry structural level was not sufficiently established or had already been invalidated."
        return structural

    @classmethod
    def _next_focus(cls, components):
        priority = ["SUPPORT_VALIDITY", "RESISTANCE_VALIDITY", "STRUCTURAL_STOP", "REWARD_RISK", "STOCK_DIRECTION", "NIFTY_ALIGNMENT", "RELATIVE_VOLUME"]
        selected = next((item for key in priority for item in components if item["component"] == key and item["score"] < item["maximum_score"]), components[0])
        return {"component": selected["component"], "current_score": selected["score"], "target_score": selected["maximum_score"], "message": selected["improvement_condition"]}
