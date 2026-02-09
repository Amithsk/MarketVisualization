#backend/app/services/step1_service.py
import logging
from datetime import date, datetime
from statistics import mean
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.schemas.step1_schema import (
    Step1PreviewResponse,
    Step1FrozenResponse,
    Step1ContextSnapshot,
    Step1ComputeRequest,
    Step1ComputeResponse,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------
# Public service methods
# -------------------------------------------------

def preview_step1_context(
    db: Session,
    trade_date: date,
) -> Step1PreviewResponse:
    """
    STEP-1 PREVIEW
    """

    logger.info("[STEP-1][PREVIEW] start trade_date=%s", trade_date)

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if existing and existing.frozen_at:
        logger.info("[STEP-1][PREVIEW] mode=AUTO")

        snapshot = Step1ContextSnapshot(
            trade_date=existing.trade_date,
            yesterday_close=existing.yesterday_close,
            yesterday_high=existing.yesterday_high,
            yesterday_low=existing.yesterday_low,
            last_5_day_ranges=existing.last_5_day_ranges or [],
            market_bias=existing.market_bias,
            gap_context=existing.gap_context,
            premarket_notes=existing.premarket_notes,
            frozen_at=existing.frozen_at,
        )

        return Step1PreviewResponse(
            mode="AUTO",
            snapshot=snapshot,
            can_freeze=False,
        )

    logger.info("[STEP-1][PREVIEW] mode=MANUAL")

    snapshot = Step1ContextSnapshot(
        trade_date=trade_date,
        last_5_day_ranges=[],
        frozen_at=None,
    )

    return Step1PreviewResponse(
        mode="MANUAL",
        snapshot=snapshot,
        can_freeze=True,
    )


def compute_step1_context(
    request: Step1ComputeRequest,
) -> Step1ComputeResponse:
    """
    STEP-1 COMPUTE (MANUAL MODE)
    """

    yc = request.yesterday_close
    yh = request.yesterday_high
    yl = request.yesterday_low
    d2h = request.day2_high
    d2l = request.day2_low
    preopen = request.preopen_price
    ranges_5d = request.last_5_day_ranges

    if yc <= 0:
        raise ValueError("Yesterday close must be > 0")

    if not ranges_5d or len(ranges_5d) < 3:
        raise ValueError("At least 3 recent daily ranges required")

    # -------------------------
    # GAP %
    # -------------------------
    gap_pct = ((preopen - yc) / yc) * 100

    # -------------------------
    # GAP CLASS
    # -------------------------
    abs_gap = abs(gap_pct)
    if abs_gap < 0.30:
        gap_class = "RANGE"
    elif abs_gap < 0.70:
        gap_class = "SELECTIVE"
    elif abs_gap < 1.0:
        gap_class = "STRONG"
    else:
        gap_class = "EVENT"

    # -------------------------
    # GAP CONTEXT (DIRECTIONAL)
    # -------------------------
    if gap_pct > 0.05:
        gap_context = "GAP_UP"
    elif gap_pct < -0.05:
        gap_context = "GAP_DOWN"
    else:
        gap_context = "FLAT"

    # -------------------------
    # RANGE RATIO
    # -------------------------
    yesterday_range = yh - yl
    avg_5d_range = mean(ranges_5d)

    range_ratio = (
        yesterday_range / avg_5d_range
        if avg_5d_range > 0
        else 0
    )

    if range_ratio < 0.8:
        range_size = "SMALL"
    elif range_ratio <= 1.2:
        range_size = "NORMAL"
    elif range_ratio <= 1.8:
        range_size = "LARGE"
    else:
        range_size = "EXTREME"

    # -------------------------
    # OVERLAP TYPE
    # -------------------------
    if yh <= d2h and yl >= d2l:
        overlap_type = "FULL"
    elif yh > d2h or yl < d2l:
        overlap_type = "NO"
    else:
        overlap_type = "PARTIAL"

    # -------------------------
    # DB2 STATE
    # -------------------------
    if range_size == "EXTREME":
        db2_state = "NO_TRADE"
    elif range_size == "SMALL" and overlap_type == "FULL":
        db2_state = "RANGE"
    elif range_size == "LARGE" and overlap_type == "NO":
        db2_state = "TREND_BIASED"
    else:
        db2_state = "UNCERTAIN"

    # -------------------------
    # SUGGESTED MARKET CONTEXT
    # -------------------------
    if db2_state == "TREND_BIASED":
        suggested_context = "TREND_DAY"
    elif db2_state == "NO_TRADE":
        suggested_context = "NO_TRADE_DAY"
    else:
        suggested_context = "RANGE_UNCERTAIN_DAY"

    return Step1ComputeResponse(
        derived_context={
            "gap_pct": round(gap_pct, 2),
            "gap_class": gap_class,
            "gap_context": gap_context,
            "range_ratio": round(range_ratio, 2),
            "range_size": range_size,
            "overlap_type": overlap_type,
            "db2_state": db2_state,
        },
        suggested_market_context=suggested_context,
    )


def freeze_step1_context(
    db: Session,
    trade_date: date,
    market_bias: str,
    gap_context: str,
    premarket_notes: str | None,
) -> Step1FrozenResponse:
    """
    STEP-1 FREEZE
    """

    logger.info("[STEP-1][FREEZE] start trade_date=%s", trade_date)

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    now = datetime.utcnow()

    if existing and existing.frozen_at:
        raise ValueError("STEP-1 is already frozen")

    if existing:
        context = existing
    else:
        context = Step1MarketContext(trade_date=trade_date)
        db.add(context)

    context.market_bias = market_bias.strip().upper()
    context.gap_context = gap_context.strip().upper()
    context.premarket_notes = premarket_notes
    context.frozen_at = now

    db.commit()
    db.refresh(context)

    snapshot = Step1ContextSnapshot(
        trade_date=context.trade_date,
        yesterday_close=context.yesterday_close,
        yesterday_high=context.yesterday_high,
        yesterday_low=context.yesterday_low,
        last_5_day_ranges=context.last_5_day_ranges or [],
        market_bias=context.market_bias,
        gap_context=context.gap_context,
        premarket_notes=context.premarket_notes,
        frozen_at=context.frozen_at,
    )

    return Step1FrozenResponse(snapshot=snapshot)
