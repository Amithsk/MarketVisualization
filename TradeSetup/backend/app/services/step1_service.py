# backend/app/services/step1_service.py

from datetime import date, datetime
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.schemas.step1_schema import (
    Step1PreviewResponse,
    Step1FrozenResponse,
    Step1ContextSnapshot,
)


# -------------------------------------------------
# Internal helpers (can be replaced later)
# -------------------------------------------------

def _get_system_market_data(trade_date: date) -> dict:
    """
    Fetch system market data required for STEP-1.
    This is a stub for now and will be replaced by real data sources.
    """
    # TODO: replace with real DB queries / data pipeline
    return {
        "prev_close": 22450.0,
        "prev_high": 22580.0,
        "prev_low": 22340.0,
        "day2_high": 22600.0,
        "day2_low": 22200.0,
        "preopen_price": 22510.0,
    }


def _derive_gap_context(prev_close: float, preopen_price: float):
    if preopen_price is None:
        return None, None

    gap_pct = ((preopen_price - prev_close) / prev_close) * 100

    if gap_pct > 0.5:
        gap_context = "GAP_UP"
    elif gap_pct < -0.5:
        gap_context = "GAP_DOWN"
    else:
        gap_context = "FLAT"

    return round(gap_pct, 2), gap_context


def _derive_range_context(prev_high: float, prev_low: float):
    range_size = prev_high - prev_low

    if range_size > 200:
        return "EXPANDED"
    elif range_size < 120:
        return "CONTRACTED"
    return "NORMAL"


# -------------------------------------------------
# Public service methods
# -------------------------------------------------

def preview_step1_context(
    db: Session,
    trade_date: date,
) -> Step1PreviewResponse:
    """
    Compute STEP-1 preview context (read-only).
    """

    # Check if already frozen
    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if existing and existing.frozen_at:
        snapshot = Step1ContextSnapshot(
            trade_date=existing.trade_date,
            prev_close=existing.prev_close,
            prev_high=existing.prev_high,
            prev_low=existing.prev_low,
            day2_high=existing.day2_high,
            day2_low=existing.day2_low,
            preopen_price=existing.preopen_price,
            gap_pct=existing.gap_pct,
            gap_context=existing.gap_context,
            range_context=existing.range_context,
            market_bias=existing.market_bias,
            premarket_notes=existing.premarket_notes,
            frozen_at=existing.frozen_at,
        )
        return Step1PreviewResponse(snapshot=snapshot, can_freeze=False)

    # Fetch system data
    system_data = _get_system_market_data(trade_date)

    gap_pct, gap_context = _derive_gap_context(
        system_data["prev_close"],
        system_data["preopen_price"],
    )

    range_context = _derive_range_context(
        system_data["prev_high"],
        system_data["prev_low"],
    )

    snapshot = Step1ContextSnapshot(
        trade_date=trade_date,
        prev_close=system_data["prev_close"],
        prev_high=system_data["prev_high"],
        prev_low=system_data["prev_low"],
        day2_high=system_data["day2_high"],
        day2_low=system_data["day2_low"],
        preopen_price=system_data["preopen_price"],
        gap_pct=gap_pct,
        gap_context=gap_context,
        range_context=range_context,
        market_bias="UNDEFINED",
        premarket_notes=None,
        frozen_at=None,
    )

    return Step1PreviewResponse(snapshot=snapshot, can_freeze=True)


def freeze_step1_context(
    db: Session,
    trade_date: date,
    market_bias: str,
    premarket_notes: str | None,
) -> Step1FrozenResponse:
    """
    Freeze STEP-1 context (irreversible).
    """

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if existing and existing.frozen_at:
        raise ValueError("STEP-1 context is already frozen")

    # Fetch system data again (authoritative)
    system_data = _get_system_market_data(trade_date)

    gap_pct, gap_context = _derive_gap_context(
        system_data["prev_close"],
        system_data["preopen_price"],
    )

    range_context = _derive_range_context(
        system_data["prev_high"],
        system_data["prev_low"],
    )

    context = Step1MarketContext(
        trade_date=trade_date,
        prev_close=system_data["prev_close"],
        prev_high=system_data["prev_high"],
        prev_low=system_data["prev_low"],
        day2_high=system_data["day2_high"],
        day2_low=system_data["day2_low"],
        preopen_price=system_data["preopen_price"],
        gap_pct=gap_pct,
        gap_context=gap_context,
        range_context=range_context,
        market_bias=market_bias,
        premarket_notes=premarket_notes,
        frozen_at=datetime.utcnow(),
    )

    db.add(context)
    db.commit()
    db.refresh(context)

    snapshot = Step1ContextSnapshot(
        trade_date=context.trade_date,
        prev_close=context.prev_close,
        prev_high=context.prev_high,
        prev_low=context.prev_low,
        day2_high=context.day2_high,
        day2_low=context.day2_low,
        preopen_price=context.preopen_price,
        gap_pct=context.gap_pct,
        gap_context=context.gap_context,
        range_context=context.range_context,
        market_bias=context.market_bias,
        premarket_notes=context.premarket_notes,
        frozen_at=context.frozen_at,
    )

    return Step1FrozenResponse(snapshot=snapshot)