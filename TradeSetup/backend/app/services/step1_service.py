# backend/app/services/step1_service.py

import logging
from datetime import date, datetime
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.schemas.step1_schema import (
    Step1PreviewResponse,
    Step1FrozenResponse,
    Step1ContextSnapshot,
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

    RULES (LOCKED):
    - Preview NEVER errors due to missing data
    - Backend explicitly decides AUTO vs MANUAL
    - Frontend must rely ONLY on `mode`
    """

    logger.info("[STEP-1][PREVIEW] trade_date=%s", trade_date)

    existing = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    # -------------------------
    # AUTO MODE
    # -------------------------
    if existing and existing.frozen_at:
        logger.info("[STEP-1][PREVIEW] AUTO mode (already frozen)")

        snapshot = Step1ContextSnapshot(
            trade_date=existing.trade_date,
            yesterday_close=existing.yesterday_close,
            yesterday_high=existing.yesterday_high,
            yesterday_low=existing.yesterday_low,
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

    # -------------------------
    # MANUAL MODE (DEFAULT)
    # -------------------------
    logger.info("[STEP-1][PREVIEW] MANUAL mode (no frozen data)")

    snapshot = Step1ContextSnapshot(
        trade_date=trade_date,
        frozen_at=None,
    )

    return Step1PreviewResponse(
        mode="MANUAL",
        snapshot=snapshot,
        can_freeze=True,
    )


def freeze_step1_context(
    db: Session,
    trade_date: date,
    market_bias: str,
    gap_context: str,
    premarket_notes: str | None,
) -> Step1FrozenResponse:
    """
    STEP-1 FREEZE (irreversible)

    RULES:
    - Accept trader input
    - Backend persists authoritative snapshot
    """

    logger.info("[STEP-1][FREEZE] trade_date=%s", trade_date)

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
        market_bias=context.market_bias,
        gap_context=context.gap_context,
        premarket_notes=context.premarket_notes,
        frozen_at=context.frozen_at,
    )

    logger.info("[STEP-1][FREEZE] completed trade_date=%s", trade_date)

    return Step1FrozenResponse(snapshot=snapshot)
