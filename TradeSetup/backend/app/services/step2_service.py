from datetime import date, datetime
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.schemas.step2_schema import (
    Step2PreviewResponse,
    Step2FrozenResponse,
    Step2OpenBehaviorSnapshot,
)


# -------------------------------------------------
# Internal helpers (rules evolve here)
# -------------------------------------------------

def _evaluate_trade_permission(
    index_open_behavior: str,
    early_volatility: str,
    market_participation: str,
) -> bool:
    """
    Decide whether trading is permitted based on observed behavior.
    Conservative by default.
    """

    if (
        index_open_behavior in ("STRONG_UP", "STRONG_DOWN")
        and market_participation == "BROAD"
        and early_volatility in ("NORMAL", "EXPANDING")
    ):
        return True

    if early_volatility == "CHAOTIC" or market_participation == "THIN":
        return False

    return False


def _to_snapshot(ctx: Step2MarketBehavior) -> Step2OpenBehaviorSnapshot:
    """
    Convert ORM object to API snapshot.
    """
    return Step2OpenBehaviorSnapshot(
        trade_date=ctx.trade_date,
        index_open_behavior=ctx.index_open_behavior,
        early_volatility=ctx.early_volatility,
        market_participation=ctx.market_participation,
        trade_allowed=ctx.trade_allowed,
        frozen_at=ctx.frozen_at,
    )


# -------------------------------------------------
# Public service methods
# -------------------------------------------------

def preview_step2_behavior(
    db: Session,
    trade_date: date,
) -> Step2PreviewResponse:
    """
    Preview STEP-2 market-open behavior (read-only).
    """

    # STEP-1 must be frozen
    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if not step1 or not step1.frozen_at:
        raise ValueError("STEP-1 must be frozen before STEP-2")

    existing = (
        db.query(Step2MarketBehavior)
        .filter(Step2MarketBehavior.trade_date == trade_date)
        .first()
    )

    # Already frozen → immutable preview
    if existing and existing.frozen_at:
        return Step2PreviewResponse(
            snapshot=_to_snapshot(existing),
            can_freeze=False,
        )

    # TODO (Phase B5):
    # - block preview outside allowed market window
    # - validate against exchange holidays

    # Default preview values (stub; replace with live feed)
    index_open_behavior = "FLAT"
    early_volatility = "UNKNOWN"
    market_participation = "UNKNOWN"

    trade_allowed = _evaluate_trade_permission(
        index_open_behavior,
        early_volatility,
        market_participation,
    )

    snapshot = Step2OpenBehaviorSnapshot(
        trade_date=trade_date,
        index_open_behavior=index_open_behavior,
        early_volatility=early_volatility,
        market_participation=market_participation,
        trade_allowed=trade_allowed,
        frozen_at=None,
    )

    return Step2PreviewResponse(snapshot=snapshot, can_freeze=True)


def freeze_step2_behavior(
    db: Session,
    trade_date: date,
    index_open_behavior: str,
    early_volatility: str,
    market_participation: str,
    trade_allowed: bool,
) -> Step2FrozenResponse:
    """
    Freeze STEP-2 market-open behavior (irreversible).
    """

    # STEP-1 must be frozen
    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if not step1 or not step1.frozen_at:
        raise ValueError("STEP-1 must be frozen before STEP-2")

    existing = (
        db.query(Step2MarketBehavior)
        .filter(Step2MarketBehavior.trade_date == trade_date)
        .first()
    )

    if existing and existing.frozen_at:
        raise ValueError("STEP-2 is already frozen")

    # Normalize inputs
    index_open_behavior = index_open_behavior.strip().upper()
    early_volatility = early_volatility.strip().upper()
    market_participation = market_participation.strip().upper()

    if existing:
        # Update existing row
        context = existing
        context.index_open_behavior = index_open_behavior
        context.early_volatility = early_volatility
        context.market_participation = market_participation
        context.trade_allowed = trade_allowed
        context.frozen_at = datetime.utcnow()
    else:
        # Insert new row
        context = Step2MarketBehavior(
            trade_date=trade_date,
            index_open_behavior=index_open_behavior,
            early_volatility=early_volatility,
            market_participation=market_participation,
            trade_allowed=trade_allowed,
            frozen_at=datetime.utcnow(),
        )
        db.add(context)

    db.commit()
    db.refresh(context)

    return Step2FrozenResponse(snapshot=_to_snapshot(context))
