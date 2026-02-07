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
# Internal helpers
# -------------------------------------------------

def _automation_available(trade_date: date) -> bool:
    """
    Stub for candidate automation availability.
    MANUAL-FIRST by default.
    """
    return False


def _generate_trade_candidates(trade_date: date) -> list[TradeCandidate]:
    """
    Deterministic AUTO candidate generation.
    """
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


def _load_persisted_candidates(
    db: Session,
    trade_date: date,
) -> list[TradeCandidate]:
    """
    Load already persisted STEP-3 candidates.
    """
    rows = (
        db.query(Step3StockSelection)
        .filter(Step3StockSelection.trade_date == trade_date)
        .all()
    )

    return [
        TradeCandidate(
            symbol=r.symbol,
            direction=r.direction,
            setup_type=r.setup_type,
            notes=r.notes,
        )
        for r in rows
    ]


# -------------------------------------------------
# Public service
# -------------------------------------------------

def generate_step3_execution(
    db: Session,
    trade_date: date,
) -> Step3ExecutionResponse:
    """
    STEP-3 — Execution Control & Candidate Selection

    LOCKED RULES:
    - Backend is source of truth
    - MANUAL-FIRST for candidates
    - Never errors due to missing automation
    - Idempotent
    """

    # -------------------------
    # Preconditions
    # -------------------------

    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )
    if not step1 or not step1.frozen_at:
        raise ValueError("STEP-1 must be frozen before STEP-3")

    step2 = (
        db.query(Step2MarketBehavior)
        .filter(Step2MarketBehavior.trade_date == trade_date)
        .first()
    )
    if not step2 or not step2.frozen_at:
        raise ValueError("STEP-2 must be frozen before STEP-3")

    # -------------------------
    # Idempotency
    # -------------------------

    existing = (
        db.query(Step3ExecutionControl)
        .filter(Step3ExecutionControl.trade_date == trade_date)
        .first()
    )

    if existing and existing.frozen_at:
        candidates = _load_persisted_candidates(db, trade_date)

        snapshot = Step3ExecutionSnapshot(
            trade_date=trade_date,
            execution_enabled=existing.execution_enabled,
            candidates_mode=(
                "AUTO" if len(candidates) > 0 else "MANUAL"
            ),
            generated_at=existing.generated_at,
            candidates=candidates,
        )
        return Step3ExecutionResponse(snapshot=snapshot)

    # -------------------------
    # STEP-3.1 — Execution Gate
    # -------------------------

    execution_enabled = step2.trade_allowed
    generated_at = datetime.utcnow()

    execution_control = Step3ExecutionControl(
        trade_date=trade_date,
        execution_enabled=execution_enabled,
        generated_at=generated_at,
        frozen_at=generated_at,
    )
    db.add(execution_control)

    candidates: list[TradeCandidate] = []
    candidates_mode = "MANUAL"

    # -------------------------
    # STEP-3.2 — Candidate Mode
    # -------------------------

    if execution_enabled and _automation_available(trade_date):
        candidates = _generate_trade_candidates(trade_date)
        candidates_mode = "AUTO"

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

    # MANUAL mode:
    # - execution_enabled may be True
    # - candidates empty
    # - frontend must allow manual entry

    db.commit()

    snapshot = Step3ExecutionSnapshot(
        trade_date=trade_date,
        execution_enabled=execution_enabled,
        candidates_mode=candidates_mode,
        generated_at=generated_at,
        candidates=candidates,
    )

    return Step3ExecutionResponse(snapshot=snapshot)
