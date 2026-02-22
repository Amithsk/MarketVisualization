# =====================================================
# File: backend/app/services/step4_service.py
# =====================================================

import logging
from datetime import datetime
from math import floor
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step3_execution_control import Step3ExecutionControl
from backend.app.models.step3_stock_selection import Step3StockSelection
from backend.app.models.step4_trade import Step4Trade
from backend.app.models.step4_trade_construction import Step4TradeConstruction

from backend.app.schemas.step4_schema import (
    Step4PreviewResponse,
    Step4ExecutionBlueprint,
    Step4ComputeRequest,
    Step4ComputeResponse,
    Step4PreviewSnapshot,
    Step4FreezeRequest,
    Step4FrozenTradeResponse,
    FrozenTradeSnapshot,
)

logger = logging.getLogger(__name__)


# =====================================================
# STEP-4 PHASE-1 → LOAD CONTEXT (STRUCTURAL ONLY)
# =====================================================

def load_step4_context(
    db: Session,
    trade_date,
) -> Step4PreviewResponse:

    logger.info(
        "[STEP4][CONTEXT][START] trade_date=%s",
        trade_date,
    )

    step3 = db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).first()

    if not step3 or not step3.execution_allowed:
        logger.info(
            "[STEP4][CONTEXT][MANUAL_REQUIRED] execution not allowed trade_date=%s",
            trade_date,
        )
        return Step4PreviewResponse(mode="MANUAL_REQUIRED", candidates=[])

    candidates = db.query(Step3StockSelection).filter(
        Step3StockSelection.trade_date == trade_date
    ).all()

    filtered = [
        c for c in candidates
        if c.strategy_used != "NO_TRADE" and bool(c.structure_valid)
    ]

    blueprints = [
        Step4ExecutionBlueprint(
            trade_date=c.trade_date,
            symbol=c.symbol,
            direction=c.direction,
            strategy_used=c.strategy_used,
            gap_high=c.gap_high,
            gap_low=c.gap_low,
            intraday_high=c.intraday_high,
            intraday_low=c.intraday_low,
            last_higher_low=c.last_higher_low,
            vwap_value=c.vwap_value,
            structure_valid=bool(c.structure_valid),
        )
        for c in filtered
    ]

    mode = "AUTO" if blueprints else "MANUAL_REQUIRED"

    logger.info(
        "[STEP4][CONTEXT][SUCCESS] trade_date=%s mode=%s candidates=%d",
        trade_date,
        mode,
        len(blueprints),
    )

    return Step4PreviewResponse(
        mode=mode,
        candidates=blueprints,
    )


# =====================================================
# STEP-4 PHASE-2 → COMPUTE (RISK + UPSERT)
# =====================================================

def compute_step4_trade(
    db: Session,
    request: Step4ComputeRequest,
) -> Step4ComputeResponse:

    trade_date = request.trade_date
    symbol = request.symbol.strip().upper()

    logger.info(
        "[STEP4][COMPUTE][START] trade_date=%s symbol=%s",
        trade_date,
        symbol,
    )

    # -------------------------------------------------
    # STEP-1 VALIDATION
    # -------------------------------------------------

    step1 = db.query(Step1MarketContext).filter(
        Step1MarketContext.trade_date == trade_date
    ).first()

    if not step1:
        raise ValueError("STEP-1 must be frozen before STEP-4")

    # -------------------------------------------------
    # STEP-2 VALIDATION
    # -------------------------------------------------

    step2 = db.query(Step2MarketBehavior).filter(
        Step2MarketBehavior.trade_date == trade_date
    ).first()

    if not step2 or not step2.trade_allowed:
        raise ValueError("Trading is not allowed for this day")

    # -------------------------------------------------
    # STEP-3 VALIDATION
    # -------------------------------------------------

    step3 = db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).first()

    if not step3 or not step3.execution_allowed:
        raise ValueError("STEP-3 execution is not enabled")

    candidate = db.query(Step3StockSelection).filter(
        Step3StockSelection.trade_date == trade_date,
        Step3StockSelection.symbol == symbol,
    ).first()

    if not candidate:
        raise ValueError("Selected symbol is not a valid STEP-3 candidate")

    direction = candidate.direction
    strategy = candidate.strategy_used
    structure_valid = bool(candidate.structure_valid)

    # -------------------------------------------------
    # STRUCTURAL DETERMINISTIC READ
    # -------------------------------------------------

    if strategy == "GAP_FOLLOW":
        if candidate.gap_high is None or candidate.gap_low is None:
            raise ValueError("Invalid GAP structure from STEP-3")

        if direction == "LONG":
            entry_price = float(candidate.gap_high) + request.entry_buffer
            stop_loss = float(candidate.gap_low)
        else:
            entry_price = float(candidate.gap_low) - request.entry_buffer
            stop_loss = float(candidate.gap_high)

    elif strategy == "MOMENTUM":
        if candidate.intraday_high is None or candidate.last_higher_low is None:
            raise ValueError("Invalid MOMENTUM structure from STEP-3")

        if direction == "LONG":
            entry_price = float(candidate.intraday_high) + request.entry_buffer
        else:
            entry_price = float(candidate.intraday_high) - request.entry_buffer

        stop_loss = float(candidate.last_higher_low)

    else:
        raise ValueError("Invalid strategy from STEP-3")

    # -------------------------------------------------
    # RISK CALCULATION
    # -------------------------------------------------

    risk_per_share = abs(entry_price - stop_loss)
    risk_amount = request.capital * (request.risk_percent / 100.0)

    trade_status = "READY"
    block_reason = None

    if risk_per_share <= 0:
        trade_status = "BLOCKED"
        block_reason = "INVALID_RISK_DISTANCE"

    quantity = floor(risk_amount / risk_per_share) if risk_per_share > 0 else 0

    if quantity < 1:
        trade_status = "BLOCKED"
        block_reason = "INSUFFICIENT_CAPITAL"

    if direction == "LONG":
        target_price = entry_price + (risk_per_share * request.r_multiple)
    else:
        target_price = entry_price - (risk_per_share * request.r_multiple)

    # -------------------------------------------------
    # UPSERT CONSTRUCTION
    # -------------------------------------------------

    construction = db.query(Step4TradeConstruction).filter(
        Step4TradeConstruction.trade_date == trade_date,
        Step4TradeConstruction.symbol == symbol,
    ).first()

    if construction:
        logger.debug("[STEP4][COMPUTE] Updating construction row")
    else:
        logger.debug("[STEP4][COMPUTE] Creating construction row")
        construction = Step4TradeConstruction(
            trade_date=trade_date,
            symbol=symbol,
        )
        db.add(construction)

    construction.strategy_used = strategy
    construction.direction = direction
    construction.structure_valid = structure_valid
    construction.entry_price = entry_price
    construction.stop_loss = stop_loss
    construction.risk_per_share = risk_per_share
    construction.quantity = quantity
    construction.target_price = target_price
    construction.trade_status = trade_status
    construction.block_reason = block_reason
    construction.constructed_at = datetime.utcnow()

    db.commit()
    db.refresh(construction)

    logger.info(
        "[STEP4][COMPUTE][SUCCESS] trade_date=%s symbol=%s status=%s qty=%d",
        trade_date,
        symbol,
        trade_status,
        quantity,
    )

    snapshot = Step4PreviewSnapshot(
        trade_date=construction.trade_date,
        symbol=construction.symbol,
        direction=construction.direction,
        strategy_used=construction.strategy_used,
        entry_price=construction.entry_price,
        stop_loss=construction.stop_loss,
        risk_per_share=construction.risk_per_share,
        quantity=construction.quantity,
        target_price=construction.target_price,
        trade_status=construction.trade_status,
        block_reason=construction.block_reason,
        constructed_at=construction.constructed_at,
    )

    return Step4ComputeResponse(preview=snapshot)


# =====================================================
# STEP-4 FREEZE (UNCHANGED CORE LOGIC)
# =====================================================

def freeze_step4_trade(
    db: Session,
    request: Step4FreezeRequest,
) -> Step4FrozenTradeResponse:

    trade_date = request.trade_date
    symbol = request.symbol.strip().upper()

    logger.info(
        "[STEP4][FREEZE][START] trade_date=%s symbol=%s",
        trade_date,
        symbol,
    )

    construction = db.query(Step4TradeConstruction).filter(
        Step4TradeConstruction.trade_date == trade_date,
        Step4TradeConstruction.symbol == symbol,
    ).first()

    if not construction:
        raise ValueError("STEP-4 compute must be generated before freeze")

    if construction.trade_status != "READY":
        raise ValueError("Cannot freeze a BLOCKED trade")

    existing_trade = db.query(Step4Trade).filter(
        Step4Trade.trade_date == trade_date,
        Step4Trade.symbol == symbol,
    ).first()

    if existing_trade:
        raise ValueError("Trade already frozen for this symbol")

    frozen_at = datetime.utcnow()

    trade = Step4Trade(
        trade_date=trade_date,
        symbol=symbol,
        direction=construction.direction,
        setup_type=construction.strategy_used,
        entry_price=construction.entry_price,
        stop_loss=construction.stop_loss,
        risk_percent=request.risk_percent,
        quantity=construction.quantity,
        rationale=request.rationale,
        frozen_at=frozen_at,
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    logger.info(
        "[STEP4][FREEZE][SUCCESS] trade_date=%s symbol=%s qty=%d",
        trade_date,
        symbol,
        trade.quantity,
    )

    snapshot = FrozenTradeSnapshot(
        trade_date=trade.trade_date,
        symbol=trade.symbol,
        direction=trade.direction,
        setup_type=trade.setup_type,
        entry_price=construction.entry_price,
        stop_loss=construction.stop_loss,
        risk_per_share=construction.risk_per_share,
        quantity=construction.quantity,
        target_price=construction.target_price,
        trade_status=construction.trade_status,
        block_reason=construction.block_reason,
        capital=request.capital,
        risk_percent=request.risk_percent,
        entry_buffer=request.entry_buffer,
        r_multiple=request.r_multiple,
        rationale=trade.rationale,
        frozen_at=trade.frozen_at,
    )

    return Step4FrozenTradeResponse(trade=snapshot)