# backend/app/services/step2_service.py

from datetime import date, datetime
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step2_market_open_behavior import Step2MarketOpenBehavior
from backend.app.schemas.step2_schema import (
    Step2PreviewResponse,
    Step2FrozenResponse,
    Step2ComputeResponse,
    Step2OpenBehaviorSnapshot,
    Step2CandleInput,
)

logger = logging.getLogger(__name__)

# =====================================================
# ANALYTICAL ENGINE
# =====================================================

def _compute_ir(candles: List[Step2CandleInput]):
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]

    ir_high = max(highs)
    ir_low = min(lows)
    ir_range = ir_high - ir_low

    return ir_high, ir_low, ir_range


def _compute_vwap(candles: List[Step2CandleInput]):
    cumulative_pv = 0
    cumulative_volume = 0
    cross_count = 0

    prev_relation = None

    for c in candles:
        typical_price = (c.high + c.low + c.close) / 3
        cumulative_pv += typical_price * c.volume
        cumulative_volume += c.volume

        vwap = cumulative_pv / cumulative_volume if cumulative_volume else typical_price

        relation = "ABOVE" if c.close > vwap else "BELOW"

        if prev_relation and relation != prev_relation:
            cross_count += 1

        prev_relation = relation

    if cross_count == 0:
        vwap_state = "ABOVE_VWAP" if prev_relation == "ABOVE" else "BELOW_VWAP"
    else:
        vwap_state = "MIXED"

    return cross_count, vwap_state


def _classify_volatility(ir_range: float, avg_5m_range_prev_day: float | None):
    if not avg_5m_range_prev_day:
        return "NORMAL"

    ratio = ir_range / avg_5m_range_prev_day

    if ratio > 1.5:
        return "EXPANDING"
    if ratio < 0.7:
        return "CONTRACTING"
    return "NORMAL"


def _range_hold_status(candles: List[Step2CandleInput], ir_high, ir_low):
    last_close = candles[-1].close

    if last_close > ir_high:
        return "BROKEN_UP"
    if last_close < ir_low:
        return "BROKEN_DOWN"
    return "HELD"


def _derive_behavior(ir_range, vwap_cross_count, volatility_state):
    if volatility_state == "EXPANDING" and vwap_cross_count == 0:
        return "STRONG_UP"
    return "WEAK_UP"


def _evaluate_trade_permission(volatility_state, range_hold_status):
    if range_hold_status == "HELD":
        return True
    return False


# =====================================================
# SNAPSHOT BUILDER
# =====================================================

def _build_snapshot(
    trade_date: date,
    mode: str,
    manual_input_required: bool,
    avg_5m_range_prev_day: float | None,
    ir_high: float | None,
    ir_low: float | None,
    ir_range: float | None,
    ir_ratio: float | None,
    volatility_state: str | None,
    vwap_cross_count: int | None,
    vwap_state: str | None,
    range_hold_status: str | None,
    index_open_behavior: str | None,
    early_volatility: str | None,
    market_participation: str | None,
    trade_allowed: bool | None,
    frozen_at=None,
):

    return Step2OpenBehaviorSnapshot(
        trade_date=trade_date,
        mode=mode,
        manual_input_required=manual_input_required,
        avg_5m_range_prev_day=avg_5m_range_prev_day,
        ir_high=ir_high,
        ir_low=ir_low,
        ir_range=ir_range,
        ir_ratio=ir_ratio,
        volatility_state=volatility_state,
        vwap_cross_count=vwap_cross_count,
        vwap_state=vwap_state,
        range_hold_status=range_hold_status,
        index_open_behavior=index_open_behavior,
        early_volatility=early_volatility,
        market_participation=market_participation,
        trade_allowed=trade_allowed,
        frozen_at=frozen_at,
    )


# =====================================================
# PREVIEW
# =====================================================

def preview_step2_behavior(db: Session, trade_date: date) -> Step2PreviewResponse:

    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if not step1:
        raise ValueError("STEP-1 must be frozen before STEP-2")

    snapshot = _build_snapshot(
        trade_date=trade_date,
        mode="MANUAL",
        manual_input_required=True,
        avg_5m_range_prev_day=None,
        ir_high=None,
        ir_low=None,
        ir_range=None,
        ir_ratio=None,
        volatility_state=None,
        vwap_cross_count=None,
        vwap_state=None,
        range_hold_status=None,
        index_open_behavior=None,
        early_volatility=None,
        market_participation=None,
        trade_allowed=None,
        frozen_at=None,
    )

    return Step2PreviewResponse(snapshot=snapshot, can_freeze=True)


# =====================================================
# COMPUTE
# =====================================================

def compute_step2_behavior(
    db: Session,
    trade_date: date,
    candles: List[Step2CandleInput],
) -> Step2ComputeResponse:

    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if not step1:
        raise ValueError("STEP-1 must be frozen before STEP-2")

    avg_5m_range_prev_day = None

    ir_high, ir_low, ir_range = _compute_ir(candles)

    ir_ratio = None
    if avg_5m_range_prev_day:
        ir_ratio = ir_range / avg_5m_range_prev_day

    volatility_state = _classify_volatility(ir_range, avg_5m_range_prev_day)

    vwap_cross_count, vwap_state = _compute_vwap(candles)

    range_hold_status = _range_hold_status(candles, ir_high, ir_low)

    index_open_behavior = _derive_behavior(
        ir_range, vwap_cross_count, volatility_state
    )

    early_volatility = volatility_state
    market_participation = "BROAD"

    trade_allowed = _evaluate_trade_permission(
        volatility_state,
        range_hold_status,
    )

    snapshot = _build_snapshot(
        trade_date=trade_date,
        mode="MANUAL",
        manual_input_required=True,
        avg_5m_range_prev_day=avg_5m_range_prev_day,
        ir_high=ir_high,
        ir_low=ir_low,
        ir_range=ir_range,
        ir_ratio=ir_ratio,
        volatility_state=volatility_state,
        vwap_cross_count=vwap_cross_count,
        vwap_state=vwap_state,
        range_hold_status=range_hold_status,
        index_open_behavior=index_open_behavior,
        early_volatility=early_volatility,
        market_participation=market_participation,
        trade_allowed=trade_allowed,
        frozen_at=None,
    )

    return Step2ComputeResponse(snapshot=snapshot, can_freeze=True)


# =====================================================
# FREEZE (DUAL TABLE PERSISTENCE)
# =====================================================

def freeze_step2_behavior(
    db: Session,
    trade_date: date,
    candles: List[Step2CandleInput],
    reason: str | None = None,
) -> Step2FrozenResponse:

    compute_response = compute_step2_behavior(
        db=db,
        trade_date=trade_date,
        candles=candles,
    )

    snapshot = compute_response.snapshot

    volatility_map = {
        "NORMAL": "NORMAL",
        "EXPANDING": "EXCESSIVE",
        "CONTRACTING": "LOW",
    }

    vwap_map = {
        "ABOVE_VWAP": "CLEAN",
        "BELOW_VWAP": "CAUTION",
        "MIXED": "CHOPPY",
    }

    range_map = {
        "HELD": "VALID",
        "BROKEN_UP": "FAILED",
        "BROKEN_DOWN": "FAILED",
    }

    trade_permission = "YES" if snapshot.trade_allowed else "NO"

    open_row = db.query(Step2MarketOpenBehavior).filter(
        Step2MarketOpenBehavior.trade_date == trade_date
    ).first()

    if not open_row:
        open_row = Step2MarketOpenBehavior(trade_date=trade_date)
        db.add(open_row)

    open_row.ir_high = snapshot.ir_high or 0.0
    open_row.ir_low = snapshot.ir_low or 0.0
    open_row.ir_range = snapshot.ir_range or 0.0
    open_row.ir_ratio = snapshot.ir_ratio or 0.0
    open_row.volatility_state = volatility_map.get(snapshot.volatility_state, "NORMAL")
    open_row.vwap_cross_count = snapshot.vwap_cross_count or 0
    open_row.vwap_state = vwap_map.get(snapshot.vwap_state, "CAUTION")
    open_row.range_hold_status = range_map.get(snapshot.range_hold_status, "NONE")
    open_row.trade_permission = trade_permission
    open_row.reason = reason or "System derived"
    open_row.decision_locked_at = datetime.utcnow()

    behavior_row = db.query(Step2MarketBehavior).filter(
        Step2MarketBehavior.trade_date == trade_date
    ).first()

    if not behavior_row:
        behavior_row = Step2MarketBehavior(trade_date=trade_date)
        db.add(behavior_row)

    behavior_row.index_open_behavior = snapshot.index_open_behavior
    behavior_row.early_volatility = snapshot.early_volatility
    behavior_row.market_participation = snapshot.market_participation
    behavior_row.trade_allowed = snapshot.trade_allowed
    behavior_row.frozen_at = datetime.utcnow()

    db.commit()

    frozen_snapshot = _build_snapshot(
        trade_date=trade_date,
        mode="AUTO",
        manual_input_required=False,
        avg_5m_range_prev_day=snapshot.avg_5m_range_prev_day,
        ir_high=snapshot.ir_high,
        ir_low=snapshot.ir_low,
        ir_range=snapshot.ir_range,
        ir_ratio=snapshot.ir_ratio,
        volatility_state=snapshot.volatility_state,
        vwap_cross_count=snapshot.vwap_cross_count,
        vwap_state=snapshot.vwap_state,
        range_hold_status=snapshot.range_hold_status,
        index_open_behavior=snapshot.index_open_behavior,
        early_volatility=snapshot.early_volatility,
        market_participation=snapshot.market_participation,
        trade_allowed=snapshot.trade_allowed,
        frozen_at=datetime.utcnow(),
    )

    return Step2FrozenResponse(snapshot=frozen_snapshot)
