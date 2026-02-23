#backend/app/services/step1_service.py
import logging
from datetime import date
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

from backend.app.services.nifty_market_data_service import (
    get_step1_structural_data,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------
# STEP-1 PREVIEW
# -------------------------------------------------

def preview_step1_context(
    db: Session,
    nifty_db: Session,
    trade_date: date,
) -> Step1PreviewResponse:

    logger.debug(
        "[STEP-1][PREVIEW] Requested for trade_date=%s",
        trade_date,
    )

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    # -------------------------------------------------
    # Case 1: Already frozen
    # -------------------------------------------------

    if existing:
        logger.debug(
            "[STEP-1][PREVIEW] Existing frozen snapshot found for trade_date=%s",
            trade_date,
        )

        snapshot = Step1ContextSnapshot(
            trade_date=existing.trade_date,
            market_bias=existing.final_market_context,
            premarket_notes=existing.final_reason,
            frozen_at=existing.created_at,
        )

        return Step1PreviewResponse(
            mode="AUTO",
            snapshot=snapshot,
            can_freeze=False,
        )

    # -------------------------------------------------
    # Case 2: No snapshot → Fetch from NIFTY DB
    # -------------------------------------------------

    logger.debug(
        "[STEP-1][PREVIEW] No snapshot found. Fetching structural data from NIFTY DB for trade_date=%s",
        trade_date,
    )

    structural_data = get_step1_structural_data(
        nifty_db=nifty_db,
        trade_date=trade_date,
    )

    logger.debug(
        "[STEP-1][PREVIEW] Structural data fetched successfully for trade_date=%s",
        trade_date,
    )

    snapshot = Step1ContextSnapshot(
        trade_date=trade_date,
        yesterday_close=structural_data["yesterday_close"],
        yesterday_high=structural_data["yesterday_high"],
        yesterday_low=structural_data["yesterday_low"],
        day2_high=structural_data["day2_high"],
        day2_low=structural_data["day2_low"],
        last_5_day_ranges=structural_data["last_5_day_ranges"],
        frozen_at=None,
    )

    return Step1PreviewResponse(
        mode="MANUAL",
        snapshot=snapshot,
        can_freeze=True,
    )


# -------------------------------------------------
# STEP-1 COMPUTE (NO PERSISTENCE)
# -------------------------------------------------

def compute_step1_context(
    request: Step1ComputeRequest,
) -> Step1ComputeResponse:

    yc = request.yesterday_close
    yh = request.yesterday_high
    yl = request.yesterday_low
    d2h = request.day2_high
    d2l = request.day2_low
    preopen = request.preopen_price
    ranges_5d = request.last_5_day_ranges

    if yc <= 0:
        raise ValueError("Yesterday close must be > 0")

    if len(ranges_5d) < 3:
        raise ValueError("At least 3 recent daily ranges required")

    gap_pct = ((preopen - yc) / yc) * 100

    abs_gap = abs(gap_pct)
    if abs_gap < 0.30:
        gap_class = "RANGE"
    elif abs_gap < 0.70:
        gap_class = "SELECTIVE"
    elif abs_gap < 1.0:
        gap_class = "STRONG"
    else:
        gap_class = "EVENT_CAUTION"

    yesterday_range = yh - yl
    avg_5d_range = mean(ranges_5d)

    range_ratio = yesterday_range / avg_5d_range

    if range_ratio < 0.8:
        range_size = "SMALL"
    elif range_ratio <= 1.2:
        range_size = "NORMAL"
    elif range_ratio <= 1.8:
        range_size = "LARGE"
    else:
        range_size = "EXTREME"

    if yh <= d2h and yl >= d2l:
        overlap_type = "FULL_OVERLAP"
    elif yh > d2h or yl < d2l:
        overlap_type = "NO_OVERLAP"
    else:
        overlap_type = "PARTIAL_OVERLAP"

    if range_size == "EXTREME":
        db2_state = "NO_TRADE"
    elif range_size == "SMALL" and overlap_type == "FULL_OVERLAP":
        db2_state = "RANGE"
    elif range_size == "LARGE" and overlap_type == "NO_OVERLAP":
        db2_state = "TREND_BIASED"
    else:
        db2_state = "UNCERTAIN"

    suggested_context = (
        "TREND_DAY"
        if db2_state == "TREND_BIASED"
        else "NO_TRADE_DAY"
        if db2_state == "NO_TRADE"
        else "RANGE_UNCERTAIN_DAY"
    )

    return Step1ComputeResponse(
        derived_context={
            "gap_pct": round(gap_pct, 2),
            "gap_class": gap_class,
            "gap_context": "GAP_UP" if gap_pct > 0.05 else "GAP_DOWN" if gap_pct < -0.05 else "FLAT",
            "range_ratio": round(range_ratio, 2),
            "range_size": range_size,
            "overlap_type": overlap_type,
            "db2_state": db2_state,
        },
        suggested_market_context=suggested_context,
    )


# -------------------------------------------------
# STEP-1 FREEZE (MAP TO EXISTING DB TABLE)
# -------------------------------------------------

def freeze_step1_context(
    db: Session,
    trade_date: date,
    preopen_price: float,
    derived_context: dict,
    market_bias: str,
    gap_context: str,
    premarket_notes: str | None,
) -> Step1FrozenResponse:

    if db.query(Step1MarketContext).filter_by(trade_date=trade_date).first():
        raise ValueError("STEP-1 is already frozen")

    context = Step1MarketContext(
        trade_date=trade_date,
        preopen_price=preopen_price,
        gap_pct=derived_context["gap_pct"],
        gap_class=derived_context["gap_class"],
        prior_range_size=derived_context["range_size"],
        prior_day_overlap=derived_context["overlap_type"],
        prior_structure_state=derived_context["db2_state"],
        final_market_context=market_bias.strip().upper(),
        final_reason=(
            premarket_notes
            or f"System gap={derived_context['gap_context']}, structure={derived_context['db2_state']}"
        ),
    )

    db.add(context)
    db.commit()
    db.refresh(context)

    snapshot = Step1ContextSnapshot(
        trade_date=context.trade_date,
        market_bias=context.final_market_context,
        premarket_notes=context.final_reason,
        frozen_at=context.created_at,
    )

    return Step1FrozenResponse(snapshot=snapshot)