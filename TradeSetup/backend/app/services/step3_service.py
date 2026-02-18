# =========================================================
# File: backend/app/services/step3_service.py
# =========================================================
"""
STEP-3 Service — Hybrid Manual Mode (Automation-Ready)

ENGINE DESIGN GUARANTEE
-----------------------

- Evaluation engine depends ONLY on Step3StockContext.
- Freeze persists ONLY deterministic evaluation result.
- Manual raw inputs are NEVER persisted.
- Future automation replaces input provider only.
"""

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
    Step3ComputeResponse,
    Step3FreezeResponse,
    Step3StockContext,
)

logger = logging.getLogger(__name__)


# =========================================================
# STEP-3A — Deterministic Matrix
# =========================================================

def _derive_step3a(market_context: str | None, trade_permission: str | None):
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

    return allowed, max_trades, execution_allowed


# =========================================================
# PREVIEW (READ ONLY)
# =========================================================

def generate_step3_execution(db: Session, trade_date: date) -> Step3ExecutionResponse:

    decided_at = datetime.utcnow()

    step1 = db.query(Step1MarketContext).filter(
        Step1MarketContext.trade_date == trade_date
    ).first()

    step2_behavior = db.query(Step2MarketBehavior).filter(
        Step2MarketBehavior.trade_date == trade_date
    ).first()

    step2_open = db.query(Step2MarketOpenBehavior).filter(
        Step2MarketOpenBehavior.trade_date == trade_date
    ).first()

    if (
        not step1
        or not step2_behavior
        or not step2_behavior.frozen_at
        or not step2_open
    ):
        return Step3ExecutionResponse(
            snapshot=Step3ExecutionSnapshot(
                trade_date=trade_date,
                market_context=None,
                trade_permission=None,
                allowed_strategies=[],
                max_trades_allowed=0,
                execution_enabled=False,
                candidates_mode="MANUAL",
                candidates=[],
                generated_at=decided_at,
            )
        )

    allowed_strategies, max_trades_allowed, execution_allowed = _derive_step3a(
        step1.final_market_context,
        step2_open.trade_permission,
    )

    existing = db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).first()

    if existing:
        rows = db.query(Step3StockSelection).filter(
            Step3StockSelection.trade_date == trade_date
        ).all()

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
                execution_enabled=bool(existing.execution_allowed),
                candidates_mode="AUTO" if candidates else "MANUAL",
                candidates=candidates,
                generated_at=existing.decided_at,
            )
        )

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
        db.rollback()

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


# =========================================================
# CORE DETERMINISTIC ENGINE
# =========================================================

def _evaluate_stock(
    context: Step3StockContext,
    allowed_strategies: list[str],
) -> tuple[TradeCandidate, float | None]:

    symbol = context.symbol.upper()

    # -------------------------
    # LAYER 1 — Tradability
    # -------------------------

    if (
        context.avg_traded_value_20d < 100
        or not (1 <= context.atr_pct <= 4)
        or context.abnormal_candle
    ):
        return (
            TradeCandidate(
                symbol=symbol,
                direction="LONG",
                strategy_used="NO_TRADE",
                reason="Rejected at Layer-1 (Tradability filter failed)",
            ),
            None,
        )

    # -------------------------
    # LAYER 2 — RS Calculation
    # -------------------------

    stock_pct = (
        (context.stock_current_price - context.stock_open_0915)
        / context.stock_open_0915
        * 100
    )

    nifty_pct = (
        (context.nifty_current_price - context.nifty_open_0915)
        / context.nifty_open_0915
        * 100
    )

    rs = stock_pct - nifty_pct

    if rs >= 0.3:
        direction = "LONG"
    elif rs <= -0.3:
        direction = "SHORT"
    else:
        return (
            TradeCandidate(
                symbol=symbol,
                direction="LONG",
                strategy_used="NO_TRADE",
                reason="Rejected at Layer-2 (RS Neutral)",
            ),
            rs,
        )

    # -------------------------
    # LAYER 3 — Strategy Fit
    # -------------------------

    strategy = "NO_TRADE"

    if (
        "GAP_FOLLOW" in allowed_strategies
        and abs(context.gap_pct) >= 1.0
        and context.gap_hold
        and context.structure_valid
    ):
        strategy = "GAP_FOLLOW"

    elif (
        "MOMENTUM" in allowed_strategies
        and context.structure_valid
        and (
            (direction == "LONG" and context.price_vs_vwap == "ABOVE")
            or (direction == "SHORT" and context.price_vs_vwap == "BELOW")
        )
    ):
        strategy = "MOMENTUM"

    if strategy == "NO_TRADE":
        return (
            TradeCandidate(
                symbol=symbol,
                direction=direction,
                strategy_used="NO_TRADE",
                reason="Rejected at Layer-3 (Strategy fit failed)",
            ),
            rs,
        )

    return (
        TradeCandidate(
            symbol=symbol,
            direction=direction,
            strategy_used=strategy,
            reason="Qualified through deterministic Layer-1/2/3 evaluation",
        ),
        rs,
    )


# =========================================================
# COMPUTE (NO PERSIST)
# =========================================================

def compute_step3_candidates(
    db: Session,
    trade_date: date,
    stocks: list[Step3StockContext],
) -> Step3ComputeResponse:

    preview = generate_step3_execution(db, trade_date)
    snapshot = preview.snapshot

    evaluated: list[TradeCandidate] = []

    for context in stocks:
        candidate, _ = _evaluate_stock(
            context,
            snapshot.allowed_strategies,
        )
        evaluated.append(candidate)

    return Step3ComputeResponse(
        snapshot=Step3ExecutionSnapshot(
            trade_date=trade_date,
            market_context=snapshot.market_context,
            trade_permission=snapshot.trade_permission,
            allowed_strategies=snapshot.allowed_strategies,
            max_trades_allowed=snapshot.max_trades_allowed,
            execution_enabled=snapshot.execution_enabled,
            candidates_mode="AUTO",
            candidates=evaluated,
            generated_at=datetime.utcnow(),
        )
    )


# =========================================================
# FREEZE (PERSIST FINAL OUTPUT ONLY)
# =========================================================

def freeze_step3_candidates(
    db: Session,
    trade_date: date,
    candidates: list[TradeCandidate],
) -> Step3FreezeResponse:

    decided_at = datetime.utcnow()

    db.query(Step3StockSelection).filter(
        Step3StockSelection.trade_date == trade_date
    ).delete()

    for c in candidates:
        db.add(
            Step3StockSelection(
                trade_date=trade_date,
                symbol=c.symbol,
                direction=c.direction,
                strategy_used=c.strategy_used,
                reason=c.reason,
                rs_value=None,  # stored if future enhancement needed
                evaluated_at=decided_at,
            )
        )

    db.commit()

    return Step3FreezeResponse(
        snapshot=Step3ExecutionSnapshot(
            trade_date=trade_date,
            market_context=None,
            trade_permission=None,
            allowed_strategies=[],
            max_trades_allowed=0,
            execution_enabled=True,
            candidates_mode="AUTO",
            candidates=candidates,
            generated_at=decided_at,
        )
    )
