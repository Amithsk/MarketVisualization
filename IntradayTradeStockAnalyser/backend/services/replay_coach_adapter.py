"""Adapt provider-core Replay Coach output into the persisted application model."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging
from typing import Any, Dict

from backend.models.replay_coach_model import (
    NoTradeAlternativePlan, ReplayCoachAnalysis, TradeAlternativePlan,
    WaitAlternativePlan,
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
    plans = []
    for plan_type, plan in (("TRADE", provider.alternative_trade_plans.trade), ("WAIT", provider.alternative_trade_plans.wait), ("NO_TRADE", provider.alternative_trade_plans.no_trade)):
        reason = _meaningful(plan.reason, "reason")
        trigger = _meaningful(plan.trigger_condition, "trigger_condition")
        invalidation = _meaningful(plan.invalidation_condition, "invalidation_condition")
        evidence_times = _evidence_times(plan.evidence_time, allowed_times)
        common = dict(entry_condition=trigger, rating=plan.rating, why_good=[reason], risks=[invalidation], evidence_times=evidence_times)
        if plan_type == "TRADE":
            entry, stop, target = (Decimal(str(plan.entry)), Decimal(str(plan.stop)), Decimal(str(plan.target)))
            side = "BUY" if plan.direction == "LONG" else "SELL"
            if side == "BUY":
                valid, risk, reward = stop < entry < target, entry - stop, target - entry
            else:
                valid, risk, reward = target < entry < stop, stop - entry, entry - target
            if not valid or risk <= 0 or reward <= 0:
                raise ValueError("TRADE prices must define positive risk and reward for its direction.")
            risk = risk.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
            reward = reward.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
            ratio = (reward / risk).quantize(RATIO_QUANTUM, rounding=ROUND_HALF_UP)
            plans.append(TradeAlternativePlan(name="Alternative Trade", plan_type="TRADE", side=side, entry_price=entry, stop_price=stop, target_price=target, numeric_explanation=f"Backend-calculated risk {risk:f}, reward {reward:f}, R:R {ratio:f}.", invalidation_condition=invalidation, risk=risk, reward=reward, risk_reward_ratio=ratio, **common))
        elif plan_type == "WAIT":
            plans.append(WaitAlternativePlan(name="Wait for Confirmation", plan_type="WAIT", confirmation_price=None, confirmation_zone=None, candle_time_condition=trigger, numeric_explanation=reason, immediate_execution_rejection=invalidation, **common))
        else:
            plans.append(NoTradeAlternativePlan(name="No Trade", plan_type="NO_TRADE", numeric_reasons=[reason], invalidating_market_stock_conditions=[invalidation], reconsideration_condition=None, **common))
    return ReplayCoachAnalysis(executed_trade_analysis=provider.executed_trade_analysis, alternative_trade_plans=plans, key_learning=provider.key_learning, limitations=provider.limitations)
