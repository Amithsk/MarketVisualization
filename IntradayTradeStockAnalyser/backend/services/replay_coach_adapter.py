"""Adapt provider-core Replay Coach output into the persisted application model."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging
from typing import Any, Dict

from backend.models.replay_coach_model import (
    FullSessionPlan, ReplayCoachAnalysis,
)
from backend.models.replay_coach_provider_model import ProviderReplayCoachTransport

MONEY_QUANTUM = Decimal("0.0001")
RATIO_QUANTUM = Decimal("0.0001")


def _meaningful(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} must be non-empty.")
    return value


def _allowed_evidence_times(context: Dict[str, Any]) -> set[str]:
    times: set[str] = set()
    for section in ("stock", "market"):
        for candle in context.get(section, {}).get("candles", []):
            value = candle.get("time")
            if isinstance(value, str):
                times.add(value)
    return times


def _evidence_times(value: str | None, allowed_times: set[str]) -> list[str]:
    """Provider evidence time is optional display metadata, never a validity gate."""
    if value is None:
        return []
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        logging.getLogger(__name__).info("Replay Coach optional evidence_time discarded: reason=INVALID_TIMESTAMP")
        return []
    normalized = parsed.isoformat(timespec="seconds")
    if normalized not in allowed_times:
        logging.getLogger(__name__).info("Replay Coach optional evidence_time discarded: reason=UNSUPPORTED_TIMESTAMP")
        return []
    return [normalized]


def to_application_analysis(provider: ProviderReplayCoachTransport, context: Dict[str, Any]) -> ReplayCoachAnalysis:
    """Validate evidence references and derive all trade arithmetic locally."""
    allowed_times = _allowed_evidence_times(context)
    plan = provider.best_full_session_plan
    decision_times = [_required_evidence_time(value, allowed_times, "decision_evidence_times") for value in plan.decision_evidence_times]
    outcome_times = [_required_evidence_time(value, allowed_times, "outcome_evidence_times") for value in plan.outcome_evidence_times]
    decision_time = _required_evidence_time(plan.decision_time, allowed_times, "decision_time")
    if decision_time and any(value > decision_time for value in decision_times): raise ValueError("decision_evidence_times cannot be after decision_time.")
    if plan.decision == "TAKE":
        entry, stop, target = float(plan.entry_price), float(plan.stop_price), float(plan.target_price)
        valid = stop < entry < target if plan.direction == "LONG" else target < entry < stop if plan.direction == "SHORT" else False
        if not valid: raise ValueError("TAKE prices must have valid direction ordering.")
        risk, reward = (entry - stop, target - entry) if plan.direction == "LONG" else (stop - entry, entry - target)
        ratio = round(reward / risk, 4)
        status = "MEETS_RULE" if ratio >= 4 else "BELOW_RULE"
    else:
        entry = stop = target = risk = reward = ratio = None; status = "NOT_APPLICABLE"
    application_values = plan.model_dump()
    application_values.update({"decision_time": decision_time, "decision_evidence_times": decision_times, "outcome_evidence_times": outcome_times, "entry_price": entry, "stop_price": stop, "target_price": target, "risk": risk, "reward": reward, "reward_to_risk": ratio, "ratio_status": status})
    application_plan = FullSessionPlan(**application_values)
    return ReplayCoachAnalysis(executed_trade_analysis=provider.executed_trade_analysis, best_full_session_plan=application_plan, key_learning=provider.key_learning, limitations=provider.limitations)


def _required_evidence_time(value: str, allowed_times: set[str], field: str) -> str:
    if not isinstance(value, str): raise ValueError(f"{field} must contain supplied candle timestamps.")
    # The provider is instructed to use canonical timestamps, but can return the
    # display clock format.  Resolve HH:mm only when it identifies one supplied
    # candle exactly; this remains evidence validation, not a guessed timestamp.
    if len(value) == 5 and value[2] == ":":
        matches = [time for time in allowed_times if time[11:16] == value]
        if len(matches) == 1:
            return matches[0]
        raise ValueError(f"{field} HH:mm must identify exactly one supplied candle timestamp.")
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error: raise ValueError(f"{field} contains an invalid timestamp.") from error
    # Some structured responses retain the supplied date and clock but omit the
    # offset.  Resolve that representation only to an exact candle on that
    # date and clock; it is not treated as an arbitrary local-time conversion.
    if parsed.tzinfo is None:
        matches = []
        for allowed in allowed_times:
            try:
                candidate = datetime.fromisoformat(allowed)
                if candidate.date() == parsed.date() and candidate.time().replace(tzinfo=None) == parsed.time():
                    matches.append(allowed)
            except ValueError:
                continue
        if len(matches) == 1:
            return matches[0]
        raise ValueError(f"{field} timestamp without timezone must identify exactly one supplied candle.")
    # Preserve the supplied canonical timestamp, while accepting an equivalent
    # instant represented with a different ISO timezone offset.
    for allowed in allowed_times:
        try:
            if datetime.fromisoformat(allowed) == parsed:
                return allowed
        except ValueError:
            continue
    raise ValueError(f"{field} must match a supplied stock or market candle timestamp.")
