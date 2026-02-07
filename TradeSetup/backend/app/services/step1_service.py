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
# Helpers
# -------------------------------------------------

def _to_snapshot(ctx: Step1MarketContext) -> Step1ContextSnapshot:
    """
    Convert ORM object to API snapshot.
    """
    return Step1ContextSnapshot(
        trade_date=ctx.trade_date,
        market_bias=ctx.final_market_context,
        gap_context=ctx.gap_class,
        premarket_notes=ctx.final_reason,
        frozen_at=ctx.created_at,
    )


# -------------------------------------------------
# Public service methods
# -------------------------------------------------

def preview_step1_context(
    db: Session,
    trade_date: date,
) -> Step1PreviewResponse:
    """
    STEP-1 Preview

    Contract:
    - MUST NOT throw if data is missing
    - MUST indicate AUTO vs MANUAL
    - No system fabrication
    """

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    # AUTO mode — data already exists
    if existing:
        return Step1PreviewResponse(
            mode="AUTO",
            snapshot=_to_snapshot(existing),
            can_freeze=False,
        )

    # MANUAL mode — no data yet (expected state)
    return Step1PreviewResponse(
        mode="MANUAL",
        snapshot=None,
        can_freeze=True,
    )


def freeze_step1_context(
    db: Session,
    trade_date: date,
    market_bias: str,
    premarket_notes: str | None,
) -> Step1FrozenResponse:
    """
    Freeze STEP-1 context (irreversible).

    Manual-only persistence.
    """

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if existing:
        raise ValueError("STEP-1 context already frozen for this date")

    context = Step1MarketContext(
        trade_date=trade_date,
        final_market_context=market_bias.strip().upper(),
        final_reason=premarket_notes or "",
        created_at=datetime.utcnow(),
    )

    db.add(context)
    db.commit()
    db.refresh(context)

    return Step1FrozenResponse(
        snapshot=_to_snapshot(context)
    )
