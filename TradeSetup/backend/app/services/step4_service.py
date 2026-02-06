from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step3_execution_control import Step3ExecutionControl
from backend.app.models.step3_stock_selection import Step3StockSelection
from backend.app.models.step4_trade import Step4Trade
from backend.app.schemas.step4_schema import (
    Step4FreezeRequest,
    Step4FrozenTradeResponse,
    FrozenTradeSnapshot,
)


def freeze_step4_trade(
    db: Session,
    request: Step4FreezeRequest,
) -> Step4FrozenTradeResponse:
    """
    Freeze final trade execution intent (irreversible).
    Money-impacting. Fully defensive.
    """

    trade_date = request.trade_date

    # -------------------------------------------------
    # STEP-1 must be frozen
    # -------------------------------------------------
    step1 = db.query(Step1MarketContext).filter(
        Step1MarketContext.trade_date == trade_date
    ).first()
    if not step1 or not step1.frozen_at:
        raise ValueError("STEP-1 must be frozen before STEP-4")

    # -------------------------------------------------
    # STEP-2 must be frozen and trade must be allowed
    # -------------------------------------------------
    step2 = db.query(Step2MarketBehavior).filter(
        Step2MarketBehavior.trade_date == trade_date
    ).first()
    if not step2 or not step2.frozen_at:
        raise ValueError("STEP-2 must be frozen before STEP-4")

    if not step2.trade_allowed:
        raise ValueError("Trading is not allowed for this day")

    # -------------------------------------------------
    # STEP-3 must be generated and execution enabled
    # -------------------------------------------------
    step3 = db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).first()
    if not step3 or not step3.execution_enabled:
        raise ValueError("STEP-3 execution is not enabled")

    # -------------------------------------------------
    # Normalize inputs
    # -------------------------------------------------
    symbol = request.symbol.strip().upper()
    direction = request.direction.strip().upper()
    execution_mode = request.execution_mode.strip().upper()
    setup_type = request.setup_type.strip().upper()

    # -------------------------------------------------
    # Symbol must exist in STEP-3 candidates
    # -------------------------------------------------
    candidate = db.query(Step3StockSelection).filter(
        Step3StockSelection.trade_date == trade_date,
        Step3StockSelection.symbol == symbol,
    ).first()
    if not candidate:
        raise ValueError("Selected symbol is not a valid STEP-3 candidate")

    # Direction + setup must match STEP-3
    if candidate.direction != direction:
        raise ValueError("Trade direction does not match STEP-3 direction")

    if candidate.setup_type != setup_type:
        raise ValueError("Setup type does not match STEP-3 setup")

    # -------------------------------------------------
    # Price sanity (capital protection)
    # -------------------------------------------------
    if direction == "LONG" and request.stop_loss >= request.entry_price:
        raise ValueError("For LONG trades, stop_loss must be below entry_price")

    if direction == "SHORT" and request.stop_loss <= request.entry_price:
        raise ValueError("For SHORT trades, stop_loss must be above entry_price")

    # -------------------------------------------------
    # STEP-4 uniqueness (per symbol per day)
    # -------------------------------------------------
    existing_trade = db.query(Step4Trade).filter(
        Step4Trade.trade_date == trade_date,
        Step4Trade.symbol == symbol,
    ).first()
    if existing_trade:
        raise ValueError("Trade for this symbol is already frozen today")

    # -------------------------------------------------
    # Freeze trade
    # -------------------------------------------------
    frozen_at = datetime.utcnow()

    trade = Step4Trade(
        trade_date=trade_date,
        symbol=symbol,
        direction=direction,
        setup_type=setup_type,
        execution_mode=execution_mode,
        entry_price=request.entry_price,
        stop_loss=request.stop_loss,
        risk_percent=request.risk_percent,
        quantity=request.quantity,
        rationale=request.rationale,
        frozen_at=frozen_at,
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    snapshot = FrozenTradeSnapshot(
        trade_date=trade.trade_date,
        symbol=trade.symbol,
        direction=trade.direction,
        setup_type=trade.setup_type,
        execution_mode=trade.execution_mode,
        entry_price=trade.entry_price,
        stop_loss=trade.stop_loss,
        risk_percent=trade.risk_percent,
        quantity=trade.quantity,
        rationale=trade.rationale,
        frozen_at=trade.frozen_at,
    )

    return Step4FrozenTradeResponse(trade=snapshot)
