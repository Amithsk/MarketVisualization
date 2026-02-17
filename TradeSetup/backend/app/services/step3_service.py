# =========================================================
# File: backend/app/services/step3_service.py
# =========================================================

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step2_market_open_behavior import Step2MarketOpenBehavior
from backend.app.models.step3_execution_control import Step3ExecutionControl
from backend.app.models.step3_stock_selection import Step3StockSelection
from backend.app.schemas.step3_schema import (
    Step3ExecutionResponse,
    Step3ExecutionSnapshot,
    TradeCandidate,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------
# STEP-3A — Deterministic Matrix (DB ALIGNED)
# -------------------------------------------------

def _derive_step3a(market_context: str, trade_permission: str):
    logger.info(
        "[STEP3][DERIVE][INPUT] context=%s permission=%s",
        market_context,
        trade_permission,
    )

    allowed: list[str] = []
    max_trades = 0

    if market_context == "TREND_DAY" and trade_permission == "YES":
        allowed = ["GAP_FOLLOW", "MOMENTUM"]
        max_trades = 3

    elif market_context == "TREND_DAY" and trade_permission == "LIMITED":
        allowed = ["MOMENTUM"]
        max_trades = 1

    elif market_context == "RANGE_UNCERTAIN_DAY" and trade_permission == "YES":
        allowed = ["MOMENTUM"]
        max_trades = 1

    elif market_context == "RANGE_UNCERTAIN_DAY" and trade_permission == "LIMITED":
        allowed = []
        max_trades = 0

    elif trade_permission == "NO":
        allowed = []
        max_trades = 0

    elif market_context == "NO_TRADE_DAY":
        allowed = []
        max_trades = 0

    execution_allowed = max_trades > 0

    logger.info(
        "[STEP3][DERIVE][RESULT] allowed=%s max_trades=%s execution_allowed=%s",
        allowed,
        max_trades,
        execution_allowed,
    )

    return allowed, max_trades, execution_allowed


# -------------------------------------------------
# Public Service
# -------------------------------------------------

def generate_step3_execution(
    db: Session,
    trade_date: date,
) -> Step3ExecutionResponse:

    logger.info("[STEP3][START] trade_date=%s", trade_date)

    # -------------------------
    # STEP-1 must exist
    # -------------------------

    step1 = (
        db.query(Step1MarketContext)
        .filter(Step1MarketContext.trade_date == trade_date)
        .first()
    )

    if not step1:
        logger.error("[STEP3][ERROR] STEP-1 missing trade_date=%s", trade_date)
        raise ValueError("STEP-1 must be frozen before STEP-3")

    # -------------------------
    # STEP-2 freeze check
    # -------------------------

    step2_behavior = (
        db.query(Step2MarketBehavior)
        .filter(Step2MarketBehavior.trade_date == trade_date)
        .first()
    )

    if not step2_behavior or not step2_behavior.frozen_at:
        logger.error("[STEP3][ERROR] STEP-2 not frozen trade_date=%s", trade_date)
        raise ValueError("STEP-2 must be frozen before STEP-3")

    # -------------------------
    # STEP-2 open decision
    # -------------------------

    step2_open = (
        db.query(Step2MarketOpenBehavior)
        .filter(Step2MarketOpenBehavior.trade_date == trade_date)
        .first()
    )

    if not step2_open:
        logger.error(
            "[STEP3][ERROR] STEP-2 open decision missing trade_date=%s",
            trade_date,
        )
        raise ValueError("STEP-2 open decision missing")

    # -------------------------
    # STEP-3A Derivation
    # -------------------------

    allowed_strategies, max_trades_allowed, execution_allowed = _derive_step3a(
        market_context=step1.final_market_context,
        trade_permission=step2_open.trade_permission,
    )

    decided_at = datetime.utcnow()

    # -------------------------
    # Idempotency Check
    # -------------------------

    existing = (
        db.query(Step3ExecutionControl)
        .filter(Step3ExecutionControl.trade_date == trade_date)
        .first()
    )

    if existing:
        logger.info("[STEP3][IDEMPOTENT] trade_date=%s", trade_date)

        rows = (
            db.query(Step3StockSelection)
            .filter(Step3StockSelection.trade_date == trade_date)
            .all()
        )

        candidates = [
            TradeCandidate(
                symbol=r.symbol,
                direction=r.direction,
                strategy_used=r.strategy_used,
                reason=r.reason,
            )
            for r in rows
        ]

        return Step3ExecutionResponse(
            snapshot=Step3ExecutionSnapshot(
                trade_date=trade_date,
                market_context=existing.market_context,
                trade_permission=existing.trade_permission,
                allowed_strategies=allowed_strategies,
                max_trades_allowed=max_trades_allowed,
                execution_enabled=execution_allowed,
                candidates_mode="AUTO" if len(candidates) > 0 else "MANUAL",
                candidates=candidates,
                generated_at=existing.decided_at,
            )
        )

    # -------------------------
    # Persist STEP-3 Decision (Race-Safe)
    # -------------------------

    logger.info("[STEP3][DB][INSERT] trade_date=%s", trade_date)

    execution_row = Step3ExecutionControl(
        trade_date=trade_date,
        market_context=step1.final_market_context,
        trade_permission=step2_open.trade_permission,
        allowed_strategies=",".join(allowed_strategies),
        max_trades_allowed=max_trades_allowed,
        execution_allowed=int(execution_allowed),
        decided_at=decided_at,
    )

    try:
        db.add(execution_row)
        db.commit()
    except IntegrityError:
        logger.warning(
            "[STEP3][DB][RACE] Duplicate insert detected trade_date=%s",
            trade_date,
        )
        db.rollback()

        existing = (
            db.query(Step3ExecutionControl)
            .filter(Step3ExecutionControl.trade_date == trade_date)
            .first()
        )

        return Step3ExecutionResponse(
            snapshot=Step3ExecutionSnapshot(
                trade_date=trade_date,
                market_context=existing.market_context,
                trade_permission=existing.trade_permission,
                allowed_strategies=allowed_strategies,
                max_trades_allowed=max_trades_allowed,
                execution_enabled=bool(existing.execution_allowed),
                candidates_mode="MANUAL",
                candidates=[],
                generated_at=existing.decided_at,
            )
        )

    logger.info(
        "[STEP3][SUCCESS] trade_date=%s execution_allowed=%s",
        trade_date,
        execution_allowed,
    )

    return Step3ExecutionResponse(
        snapshot=Step3ExecutionSnapshot(
            trade_date=trade_date,
            market_context=step1.final_market_context,
            trade_permission=step2_open.trade_permission,
            allowed_strategies=allowed_strategies,
            max_trades_allowed=max_trades_allowed,
            execution_enabled=execution_allowed,
            candidates_mode="MANUAL",
            candidates=[],
            generated_at=decided_at,
        )
    )
