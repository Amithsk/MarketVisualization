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
# STEP-3A — Deterministic Matrix (FROZEN)
# -------------------------------------------------

def _derive_step3a(step1_context: str, trade_permission: str):
    """
    Derives:
    - allowed_strategies
    - max_trades_allowed
    - execution_enabled
    """

    allowed: list[str] = []
    max_trades = 0

    if step1_context == "TREND" and trade_permission == "YES":
        allowed = ["GAP_FOLLOW", "MOMENTUM"]
        max_trades = 3

    elif step1_context == "TREND" and trade_permission == "LIMITED":
        allowed = ["MOMENTUM"]
        max_trades = 1

    elif step1_context == "RANGE" and trade_permission == "YES":
        allowed = ["MOMENTUM"]
        max_trades = 1

    elif step1_context == "RANGE" and trade_permission == "LIMITED":
        allowed = []
        max_trades = 0

    elif trade_permission == "NO":
        allowed = []
        max_trades = 0

    elif step1_context == "NO_TRADE":
        allowed = []
        max_trades = 0

    execution_enabled = max_trades > 0

    return allowed, max_trades, execution_enabled


# -------------------------------------------------
# Automation Stubs (MANUAL-FIRST)
# -------------------------------------------------

def _automation_available(trade_date: date) -> bool:
    """
    MANUAL-FIRST.
    Replace when automation pipeline is ready.
    """
    return False


def _generate_trade_candidates(trade_date: date) -> list[TradeCandidate]:
    """
    Deterministic AUTO candidate generation stub.
    Must comply with final schema.
    """
    return [
        TradeCandidate(
            symbol="RELIANCE",
            direction="LONG",
            strategy_used="MOMENTUM",
            reason="Relative strength aligned and structure intact.",
        ),
        TradeCandidate(
            symbol="TCS",
            direction="SHORT",
            strategy_used="GAP_FOLLOW",
            reason="Gap aligned with direction and holding above structure.",
        ),
    ]


def _load_persisted_candidates(
    db: Session,
    trade_date: date,
) -> list[TradeCandidate]:

    rows = (
        db.query(Step3StockSelection)
        .filter(Step3StockSelection.trade_date == trade_date)
        .all()
    )

    return [
        TradeCandidate(
            symbol=r.symbol,
            direction=r.direction,
            strategy_used=r.strategy_used,
            reason=r.reason,
        )
        for r in rows
    ]


# -------------------------------------------------
# Public Service
# -------------------------------------------------

def generate_step3_execution(
    db: Session,
    trade_date: date,
) -> Step3ExecutionResponse:
    """
    STEP-3 — Execution Control & Stock Selection

    LOCKED RULES:
    - Backend is source of truth
    - STEP-3A always computed
    - STEP-3B always activated after freeze
    - MANUAL mode if automation unavailable
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
    # STEP-3A — Always Derived
    # -------------------------

    allowed_strategies, max_trades_allowed, execution_enabled = _derive_step3a(
        step1_context=step1.market_context,
        trade_permission=step2.trade_permission,
    )

    generated_at = datetime.utcnow()

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
            allowed_strategies=allowed_strategies,
            max_trades_allowed=max_trades_allowed,
            execution_enabled=execution_enabled,
            candidates_mode=(
                "AUTO" if len(candidates) > 0 else "MANUAL"
            ),
            candidates=candidates,
            generated_at=existing.generated_at,
        )

        return Step3ExecutionResponse(snapshot=snapshot)

    # -------------------------
    # Persist Execution Control
    # -------------------------

    execution_control = Step3ExecutionControl(
        trade_date=trade_date,
        execution_enabled=execution_enabled,
        generated_at=generated_at,
        frozen_at=generated_at,
    )

    db.add(execution_control)

    # -------------------------
    # STEP-3B — Candidate Mode
    # -------------------------

    candidates: list[TradeCandidate] = []
    candidates_mode = "MANUAL"

    if _automation_available(trade_date):
        candidates = _generate_trade_candidates(trade_date)
        candidates_mode = "AUTO"

        for c in candidates:
            db.add(
                Step3StockSelection(
                    trade_date=trade_date,
                    symbol=c.symbol,
                    direction=c.direction,
                    strategy_used=c.strategy_used,
                    reason=c.reason,
                )
            )

    db.commit()

    snapshot = Step3ExecutionSnapshot(
        trade_date=trade_date,
        allowed_strategies=allowed_strategies,
        max_trades_allowed=max_trades_allowed,
        execution_enabled=execution_enabled,
        candidates_mode=candidates_mode,
        candidates=candidates,
        generated_at=generated_at,
    )

    return Step3ExecutionResponse(snapshot=snapshot)
