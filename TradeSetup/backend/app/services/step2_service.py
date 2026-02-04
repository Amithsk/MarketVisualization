# backend/app/services/step2_service.py

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
# Internal helpers (rules can evolve here)
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

    # Strong trend + broad participation → trade allowed
    if (
        index_open_behavior in ("STRONG_UP", "STRONG_DOWN")
        and market_participation == "BROAD"
        and early_volatility in ("NORMAL", "EXPANDING")
    ):
        return True

    # Chaotic volatility or thin participation → no trade
    if early_volatility == "CHAOTIC" or market_participation == "THIN":
        return False

    # Default: no trade
    return False


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

    # If STEP-2 already frozen, return it
    existing = (
        db.query(Step2MarketBehavior)
        .filter(Step2MarketBehavior.trade_date == trade_date)
        .first()
    )

    if existing and existing.frozen_at:
        snapshot = Step2OpenBehaviorSnapshot(
            trade_date=existing.trade_date,
            index_open_behavior=existing.index_open_behavior,
            early_volatility=existing.early_volatility,
            market_participation=existing.market_participation,
            trade_allowed=existing.trade_allowed,
            frozen_at=existing.frozen_at,
        )
        return Step2PreviewResponse(snapshot=snapshot, can_freeze=False)

    # Default preview values (to be replaced by live data later)
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

    snapshot = Step2OpenBehaviorSnapshot(
        trade_date=context.trade_date,
        index_open_behavior=context.index_open_behavior,
        early_volatility=context.early_volatility,
        market_participation=context.market_participation,
        trade_allowed=context.trade_allowed,
        frozen_at=context.frozen_at,
    )

    return Step2FrozenResponse(snapshot=snapshot)