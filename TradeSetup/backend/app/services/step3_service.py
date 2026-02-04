# backend/app/services/step3_service.py

from datetime import date, datetime
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step3_execution_control import Step3ExecutionControl
from backend.app.models.step3_stock_selection import Step3StockSelection
from backend.app.schemas.step3_schema import (
    Step3ExecutionResponse,
    Step3ExecutionSnapshot,
    TradeCandidate,
)


# -------------------------------------------------
# Internal helpers (deterministic rules)
# -------------------------------------------------

def _generate_trade_candidates(trade_date: date) -> list[TradeCandidate]:
    """
    Deterministically generate trade candidates.
    This is a stub — replace with your real selection logic later.
    """

    # Example deterministic output (placeholder)
    return [
        TradeCandidate(
            symbol="RELIANCE",
            direction="LONG",
            setup_type="TREND_CONTINUATION",
            notes="Strong relative strength",
        ),
        TradeCandidate(
            symbol="TCS",
            direction="SHORT",
            setup_type="MEAN_REVERSION",
            notes="Extended opening range",
        ),
    ]


# -------------------------------------------------
# Public service method
# -------------------------------------------------

def generate_step3_execution(
    db: Session,
    trade_date: date,
) -> Step3ExecutionResponse:
    """
    Generate STEP-3 execution control & stock selection.
    Read-only and deterministic.
    """

    # STEP-1 must be frozen
    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if not step1 or not step1.frozen_at:
        raise ValueError("STEP-1 must be frozen before STEP-3")

    # STEP-2 must be frozen
    step2 = (
        db.query(Step2MarketBehavior)
        .filter(Step2MarketBehavior.trade_date == trade_date)
        .first()
    )

    if not step2 or not step2.frozen_at:
        raise ValueError("STEP-2 must be frozen before STEP-3")

    execution_enabled = step2.trade_allowed

    # Clear previous STEP-3 data (regeneration allowed)
    db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).delete()

    db.query(Step3StockSelection).filter(
        Step3StockSelection.trade_date == trade_date
    ).delete()

    generated_at = datetime.utcnow()

    # Persist execution control
    execution_control = Step3ExecutionControl(
        trade_date=trade_date,
        execution_enabled=execution_enabled,
        generated_at=generated_at,
    )
    db.add(execution_control)

    candidates: list[TradeCandidate] = []

    if execution_enabled:
        candidates = _generate_trade_candidates(trade_date)

        for c in candidates:
            db.add(
                Step3StockSelection(
                    trade_date=trade_date,
                    symbol=c.symbol,
                    direction=c.direction,
                    setup_type=c.setup_type,
                    notes=c.notes,
                )
            )

    db.commit()

    snapshot = Step3ExecutionSnapshot(
        trade_date=trade_date,
        execution_enabled=execution_enabled,
        generated_at=generated_at,
        candidates=candidates,
    )

    return Step3ExecutionResponse(snapshot=snapshot)