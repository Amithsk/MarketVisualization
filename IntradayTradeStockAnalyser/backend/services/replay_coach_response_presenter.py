"""Present canonical Replay Coach analysis safely for the public API."""
from copy import deepcopy
from datetime import datetime
import re
from typing import Any
from zoneinfo import ZoneInfo

from backend.models.replay_coach_model import CoachChecklistRow, CoachDecisionOption, CoachDisplay, CoachDisplayRow, CoachDisplaySection, CoachPlanDisplay, CoachPlanRow, ExecutedTradeVerdict, ExecutedTradeVerdictRow, ReplayCoachAnalysis
from backend.services.replay_coach_scoring_service import ReplayCoachScoringService


IST = ZoneInfo("Asia/Kolkata")
# Complete ISO datetimes only.  This deliberately excludes plain clock times,
# dates, prices, ratios, and partial timestamp-like values.
ISO_TIMESTAMP = re.compile(
    r"(?<![A-Za-z0-9_])\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})(?![A-Za-z0-9_])"
)


class ReplayCoachResponsePresenter:
    """Converts timestamps in response-only analysis content to IST HH:mm."""

    @classmethod
    def present(cls, analysis: ReplayCoachAnalysis) -> dict[str, Any]:
        """Return a display copy; never mutate the validated canonical model."""
        payload = deepcopy(analysis.model_dump(mode="json"))
        return cls._present_value(payload)

    @classmethod
    def coach_display(cls, analysis: ReplayCoachAnalysis, context: dict[str, Any], decision_quality: dict[str, Any] | None = None) -> dict[str, Any]:
        """Build the compact, deterministic view without changing canonical JSON."""
        decision_quality = decision_quality or ReplayCoachScoringService.score(context)
        facts = context.get("decision_context", {}); economics = facts.get("risk_economics", {})
        timing = facts.get("decision_timing", {}); stock = facts.get("stock_direction", {})
        nifty = facts.get("nifty_direction", {}); volume = facts.get("stock_relative_volume", {})
        levels = facts.get("support_resistance", []); trade = context.get("executed_trade", {})
        time = timing.get("last_completed_stock_candle_time")
        ratio = economics.get("reward_risk_ratio"); required = economics.get("required_ratio", 4.0)
        support = next((level for level in levels if level.get("level_type") == "SUPPORT" and level.get("level", 0) < (economics.get("entry") or float("inf"))), None)
        structural_stop = support and economics.get("stop") is not None and economics["stop"] <= support["level"]
        take_valid = bool(economics.get("take_valid") and structural_stop)
        direction_score = 2 if stock.get("classification") in ("BULLISH", "BEARISH") else 1 if stock.get("classification") == "NEUTRAL" else 0
        nifty_score = 2 if nifty.get("classification") in ("BULLISH", "BEARISH") else 1 if nifty.get("classification") == "NEUTRAL" else 0
        vol_ratio = volume.get("ratio_vs_5_candle_median")
        volume_score = 2 if vol_ratio is not None and vol_ratio >= 1.5 else 1 if vol_ratio is not None and vol_ratio >= 1 else 0
        structure_score = 2 if structural_stop else 1 if support else 0
        rr_score = 2 if ratio is not None and ratio >= 4 else 1 if ratio is not None and ratio >= 2 else 0
        scores = [direction_score, nifty_score, volume_score, structure_score, rr_score]
        total = sum(scores)
        def row(component, value, score, explanation, status="MIXED", times=None):
            return CoachDisplayRow(component=component, value=value, rating=score, explanation=explanation, graph_times=times or ([time] if time else []), status=status)
        ratios = "Not established" if vol_ratio is None else f"{vol_ratio:.2f}× five-candle median"
        component_rows = [
            row("Direction", stock.get("classification", "Unavailable"), direction_score, f"Completed close {stock.get('last_completed_close', 'unavailable')} versus VWAP {stock.get('vwap', 'unavailable')}; direction evidence {'aligns' if direction_score == 2 else 'is mixed or unavailable'}.", "CONFIRMED" if direction_score == 2 else "MIXED"),
            row("NIFTY alignment", nifty.get("classification", "Unavailable"), nifty_score, f"NIFTY completed-candle direction is {nifty.get('classification', 'unavailable')}; this {'supports' if nifty_score == 2 else 'does not fully confirm'} the decision.", "CONFIRMED" if nifty_score == 2 else "MIXED"),
            row("Relative volume", ratios, volume_score, f"Completed stock volume {volume.get('last_completed_volume', 'unavailable')} compared only with its own five-candle median; {'confirmation exists' if volume_score == 2 else 'do not award volume confirmation'}.", "CONFIRMED" if volume_score == 2 else "NOT_ESTABLISHED"),
            row("Structure", "Established support" if structural_stop else "Not established from pre-entry evidence", structure_score, "Support requires two completed-candle touches and a structural stop; arithmetic-only stops are not valid.", "CONFIRMED" if structural_stop else "NOT_ESTABLISHED"),
            row("Risk/reward", f"{ratio:.2f}:1" if ratio is not None else "Unavailable", rr_score, f"Reward/risk {ratio if ratio is not None else 'unavailable'} versus required {required}:1; {'TAKE passes' if economics.get('take_valid') else 'TAKE fails'} the price-risk rule.", "CONFIRMED" if rr_score == 2 else "CONFLICTING"),
        ]
        executed_rows = [
            row("Direction", f"{context.get('documented_plan', {}).get('position_type') or trade.get('side', 'Unknown')} / executed {trade.get('side', 'Unknown')}", total, "Original decision quality is scored from completed pre-entry evidence.", times=[]),
            row("Entry", f"₹{trade.get('entry_price', 'Unavailable')} at {trade.get('entry_timestamp', 'Unavailable')}", total, "Actual execution entry.", times=[]),
            row("Stop / Target", f"₹{economics.get('stop', 'Unavailable')} / ₹{economics.get('target', 'Unavailable')}", total, "Documented plan levels.", times=[]),
            row("Risk / Reward", f"₹{economics.get('risk', 'Unavailable')} / ₹{economics.get('reward', 'Unavailable')}", rr_score, f"R:R {ratio if ratio is not None else 'unavailable'} versus required {required}:1.", times=[]),
            row("Break-even / recovery", f"{(economics.get('break_even_win_rate') or 0) * 100:.0f}% / {economics.get('equal_wins_to_recover_one_loss', 'Unavailable')}", rr_score, "Backend risk economics; profitable outcome does not improve entry quality.", times=[]),
            row("Result", f"₹{trade.get('pnl_amount', 'Unavailable')} on quantity {trade.get('quantity', 'Unavailable')}", total, "Execution outcome is separate from the entry decision.", times=[]),
            row("Verdict", "Profitable outcome, but original plan failed the 1:4 rule." if not economics.get("take_valid") else "Original plan met the documented price-risk rule.", total, "Based on decision-time evidence and documented plan.", times=[]),
        ]
        executed = CoachDisplaySection(title="Executed Trade Verdict", decision="EXECUTED", overall_rating=total, valid=take_valid, rows=executed_rows)
        executed = cls._executed_trade_verdict(context, economics, required)
        take = CoachDisplaySection(title="Take the Trade", decision="TAKE", overall_rating=total, valid=take_valid, rows=component_rows)
        wait_rows = component_rows + [row("Wait condition", f"Evaluate after {timing.get('containing_candle_end', 'next completed candle')}", total, "The entry candle was incomplete; wait for a completed candle, volume baseline confirmation, and structural stop.", "WAIT")]
        wait = CoachDisplaySection(title="Wait for Confirmation", decision="WAIT", overall_rating=10-total if not take_valid else total, valid=True, rows=wait_rows)
        no_trade = CoachDisplaySection(title="No Trade", decision="NO_TRADE", overall_rating=10-total if not take_valid else max(0, 6-total), valid=True, rows=component_rows)
        best = wait if not take_valid else take
        best_section, decision_options = cls._decision_presentations(context, economics, timing, stock, nifty, volume, structural_stop, ratio, required, take_valid)
        checklist = cls._recommended_checklist(timing, stock, nifty, volume, structural_stop, ratio, required, context)
        pnl = trade.get("pnl_amount")
        profitable = isinstance(pnl, (int, float)) and pnl >= 0
        result = {
            "status": "PROFITABLE" if profitable else "LOSS",
            "pnl_amount": float(pnl) if isinstance(pnl, (int, float)) else None,
            "summary": f"{'Target reached; ' if profitable else ''}₹{abs(float(pnl or 0)):,.2f} {'profit' if profitable else 'loss'}."
        }
        shared_times = [time[11:16]] if isinstance(time, str) and len(time) >= 16 else []
        score_display = {key: value for key, value in decision_quality.items() if key != "next_trade_focus"}
        return cls._present_value(CoachDisplay(
            trade_result=result,
            decision_quality_score=score_display,
            next_trade_focus=decision_quality["next_trade_focus"],
            shared_graph_times=shared_times,
            execution_times={key: value for key, value in {"entry": trade.get("entry_timestamp"), "exit": trade.get("exit_timestamp")}.items() if value},
            executed_trade_verdict=executed,
            my_best_trade_plan=best_section,
            decision_options=decision_options,
            recommended_decision_checklist=checklist,
        ).model_dump(mode="json"))

    @staticmethod
    def _decision_presentations(context, economics, timing, stock, nifty, volume, structural_stop, ratio, required, take_valid):
        """Build concise, deterministic action guidance; provider ratings never affect it."""
        side = (context.get("documented_plan", {}).get("position_type") or "LONG").upper()
        direction = f"{side} candidate" if stock.get("classification") in ("BULLISH", "BEARISH") else "Not established from pre-entry evidence."
        volume_ratio = volume.get("ratio_vs_5_candle_median")
        volume_value = "Not established from pre-entry evidence." if volume_ratio is None else f"{volume_ratio:.2f}× baseline"
        median_volume = volume.get("previous_5_candle_median")
        required_volume = median_volume * 1.2 if isinstance(median_volume, (int, float)) else None
        volume_requirement = (f"At least 1.20× / {required_volume:,.0f} shares" if required_volume is not None else "Required volume was not established from pre-entry evidence.")
        volume_detail = (f"Completed volume {volume.get('last_completed_volume', 'unavailable'):,.0f} versus required {required_volume:,.0f} shares." if isinstance(volume.get("last_completed_volume"), (int, float)) and required_volume is not None else "Completed volume or its baseline was not established from pre-entry evidence.")
        stop_detail = "A chart-supported structural stop was established." if structural_stop else "No chart-supported structural stop was established from pre-entry evidence."
        rr_detail = (f"Current {ratio:.2f}:1 versus required {required:.0f}:1; shortfall {max(0, required-ratio):.2f}." if isinstance(ratio, (int, float)) else "Reward-to-risk was not established from pre-entry evidence.")
        review = timing.get("containing_candle_end") or "Not established from pre-entry evidence."
        rr = f"{ratio:.2f}:1" if isinstance(ratio, (int, float)) else "Not established from pre-entry evidence."
        structural = "Established" if structural_stop else "Not confirmed"
        common = [
            CoachPlanRow(component="Direction", recommendation=direction, explanation="Use completed-candle direction and VWAP before entering."),
            CoachPlanRow(component="NIFTY support", recommendation=stock.get("classification", "Neutral") if nifty.get("classification") is None else nifty.get("classification", "Neutral").title(), explanation="NIFTY support is based only on completed market candles."),
            CoachPlanRow(component="Volume", recommendation=volume_value, explanation=volume_detail),
            CoachPlanRow(component="Structure", recommendation=structural, explanation=stop_detail),
            CoachPlanRow(component="Current R:R", recommendation=rr, explanation=rr_detail),
        ]
        wait_rows = common + [
            CoachPlanRow(component="Earliest review", recommendation=f"After {review}", explanation="Recheck the completed candle, volume, structural stop, and reward-to-risk together."),
            CoachPlanRow(component="Confirmation", recommendation="Completed candle confirmation required", explanation="Use only a backend-established level; no confirmation price is invented."),
            CoachPlanRow(component="Final action", recommendation="WAIT", explanation=f"After {review}, inspect the completed candle, {volume_requirement}, structural stop, and {required:.0f}:1 reward-to-risk."),
        ]
        best_decision = "TAKE" if take_valid else "WAIT"
        best = CoachPlanDisplay(title="My Best Trade Plan", decision=best_decision, status_label="READY" if take_valid else "WAIT", rows=(common + [CoachPlanRow(component="Best decision", recommendation=best_decision, explanation="All mandatory checks pass." if take_valid else "Mandatory confirmation is still missing."), CoachPlanRow(component="Final action", recommendation=best_decision, explanation="Enter only when the stop is structural and the plan remains at least 4:1.")]) if take_valid else wait_rows)
        checks = ["Current status", "What it means", "Direction requirement", "Candle requirement", "Volume requirement", "Structure requirement", "R:R requirement", "Action now", "Becomes valid when", "Cancel when"]
        values = {
            "TAKE": ["READY" if take_valid else "NOT READY", "Enter now" if take_valid else f"Do not enter: {volume_detail} {stop_detail} {rr_detail}", f"{side} remains valid", f"Completed at {review}", volume_requirement, structural, f"Current {rr}; required {required:.0f}:1", "Enter" if take_valid else "Do not enter", f"Completed candle, {volume_requirement}, structural stop, and {required:.0f}:1 are all present", f"Cancel if the completed candle, volume, structure, or {required:.0f}:1 ratio fails"],
            "WAIT": ["NOT RECOMMENDED" if take_valid else "RECOMMENDED", f"Re-evaluate after {review}", f"Completed {side} confirmation", f"Candle closes at {review}", volume_requirement, "Confirmed chart level and retest", f"Recalculate to at least {required:.0f}:1", f"Wait until {review}", f"Completed candle shows {side}, {volume_requirement}, structural stop, and {required:.0f}:1", f"Cancel if the completed candle removes {side} support or no structural stop can keep {required:.0f}:1"],
            "NO_TRADE": ["NOT REQUIRED" if take_valid else "VALID ALTERNATIVE", f"Skip: {volume_detail} {stop_detail} {rr_detail}", f"{side} direction must be confirmed", f"No qualifying completed candle before {review}", volume_requirement, "No structural stop from pre-entry evidence", f"Current {rr} is below {required:.0f}:1", "Skip this setup", f"Use when a new completed setup later has {volume_requirement}, structure, and {required:.0f}:1", "Reconsider only after a separate completed setup forms"],
        }
        titles = {"TAKE": "Take the Trade", "WAIT": "Wait for Confirmation", "NO_TRADE": "No Trade"}
        options = [CoachDecisionOption(title=titles[decision], decision=decision, status=values[decision][0], rows=[CoachPlanRow(component=check, recommendation=value, explanation="") for check, value in zip(checks, values[decision])]) for decision in ("TAKE", "WAIT", "NO_TRADE")]
        return best, options

    @staticmethod
    def _recommended_checklist(timing, stock, nifty, volume, structural_stop, ratio, required, context):
        side = (context.get("documented_plan", {}).get("position_type") or "LONG").upper()
        median, current = volume.get("previous_5_candle_median"), volume.get("last_completed_volume")
        required_volume = median * 1.2 if isinstance(median, (int, float)) else None
        completed = timing.get("containing_candle_complete_at_entry") is True
        return [
            CoachChecklistRow(check="Candle completed", current_value="Yes" if completed else f"No at {timing.get('entry_time', 'unavailable')}", required_value=f"Yes, after {timing.get('containing_candle_end', 'unavailable')}", status="PASS" if completed else "WAIT"),
            CoachChecklistRow(check="Stock direction", current_value=str(stock.get("classification", "Not established")).title(), required_value=f"{side.title()} for {side}", status="PASS" if (side == "LONG" and stock.get("classification") == "BULLISH") or (side == "SHORT" and stock.get("classification") == "BEARISH") else "FAIL"),
            CoachChecklistRow(check="NIFTY alignment", current_value=str(nifty.get("classification", "Not established")).title(), required_value=f"{side.title()} preferred", status="PASS" if nifty.get("classification") == ("BULLISH" if side == "LONG" else "BEARISH") else "PARTIAL" if nifty.get("classification") == "NEUTRAL" else "FAIL"),
            CoachChecklistRow(check="Relative volume", current_value=f"{volume.get('ratio_vs_5_candle_median'):.2f}×" if isinstance(volume.get("ratio_vs_5_candle_median"), (int, float)) else "Not established from pre-entry evidence.", required_value=f"1.20× / {required_volume:,.0f} shares" if required_volume is not None else "Not established from pre-entry evidence.", status="PASS" if isinstance(current, (int, float)) and required_volume is not None and current >= required_volume else "FAIL"),
            CoachChecklistRow(check="Structural stop", current_value="Established" if structural_stop else "Not established from pre-entry evidence.", required_value="Chart-supported stop required", status="PASS" if structural_stop else "FAIL"),
            CoachChecklistRow(check="Reward-to-risk", current_value=f"{ratio:.2f}:1" if isinstance(ratio, (int, float)) else "Not established from pre-entry evidence.", required_value=f"At least {required:.0f}:1", status="PASS" if isinstance(ratio, (int, float)) and ratio >= required else "FAIL"),
        ]

    @classmethod
    def _present_value(cls, value: Any, field_name: str | None = None) -> Any:
        if isinstance(value, dict):
            return {key: cls._present_value(item, key) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._present_value(item, field_name) for item in value]
        if isinstance(value, str):
            if value == "documented_plan" and field_name in {"time", "evidence_times"}:
                return "Plan"
            return ISO_TIMESTAMP.sub(cls._format_timestamp, value)
        return value

    @staticmethod
    def _executed_trade_verdict(context: dict[str, Any], economics: dict[str, Any], required: float) -> ExecutedTradeVerdict:
        """Present factual execution economics separately from decision quality."""
        trade, plan = context.get("executed_trade", {}), context.get("documented_plan", {})
        position = (plan.get("position_type") or "").upper()
        side = "LONG" if position == "LONG" else "SHORT" if position == "SHORT" else ("LONG" if trade.get("side") == "BUY" else "SHORT")
        entry = economics.get("entry", trade.get("entry_price")); stop, target = economics.get("stop"), economics.get("target")
        risk = reward = ratio = None
        if all(isinstance(value, (int, float)) for value in (entry, stop, target)):
            risk = float(entry) - float(stop) if side == "LONG" else float(stop) - float(entry)
            reward = float(target) - float(entry) if side == "LONG" else float(entry) - float(target)
            ratio = reward / risk if risk > 0 else None
        quantity = trade.get("quantity")
        planned_risk = risk * quantity if isinstance(risk, (int, float)) and isinstance(quantity, (int, float)) else None
        planned_reward = reward * quantity if isinstance(reward, (int, float)) and isinstance(quantity, (int, float)) else None
        pnl = trade.get("pnl_amount")
        profitable = isinstance(pnl, (int, float)) and pnl >= 0
        plan_standard = "MEETS_REQUIRED_RR" if ratio is not None and ratio >= required else "BELOW_REQUIRED_RR"
        def money(value: Any) -> str: return "Unavailable" if value is None else f"₹{float(value):,.2f}"
        rows = [
            ExecutedTradeVerdictRow(component="Direction", value=f"{side} / {trade.get('side', 'Unknown')}", meaning="Expected the price to rise." if side == "LONG" else "Expected the price to fall."),
            ExecutedTradeVerdictRow(component="Entry", value=f"{money(trade.get('entry_price'))} at {trade.get('entry_timestamp', 'Unavailable')}", meaning="Actual executed entry."),
            ExecutedTradeVerdictRow(component="Stop", value=money(stop), meaning=f"{money(risk)} planned risk per share."),
            ExecutedTradeVerdictRow(component="Target", value=money(target), meaning=f"{money(reward)} planned reward per share."),
            ExecutedTradeVerdictRow(component="Planned risk", value=money(planned_risk), meaning="Planned risk per share × quantity."),
            ExecutedTradeVerdictRow(component="Planned reward", value=money(planned_reward), meaning="Planned reward per share × quantity."),
            ExecutedTradeVerdictRow(component="Reward-to-risk", value=f"{ratio:.2f}:1" if ratio is not None else "Unavailable", meaning="Planned reward for every ₹1 risked."),
            ExecutedTradeVerdictRow(component="Result", value=("+" if profitable else "-") + money(abs(float(pnl))) if isinstance(pnl, (int, float)) else "Unavailable", meaning="Actual trade result."),
            ExecutedTradeVerdictRow(component="Verdict", value="Profitable result, weak original plan" if profitable and plan_standard == "BELOW_REQUIRED_RR" else ("Profitable result" if profitable else "Loss result"), meaning="The outcome is separate from whether the plan met the 1:4 rule."),
        ]
        return ExecutedTradeVerdict(outcome_status="PROFITABLE" if profitable else "LOSS", plan_standard_status=plan_standard, rows=rows)

    @staticmethod
    def _format_timestamp(match: re.Match[str]) -> str:
        raw = match.group(0)
        try:
            parsed = datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
            return parsed.astimezone(IST).strftime("%H:%M")
        except ValueError:
            # A syntactically timestamp-like but invalid value is retained.
            return raw
