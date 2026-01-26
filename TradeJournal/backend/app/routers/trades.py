# app/routers/trades.py

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db

router = APIRouter(prefix="/api", tags=["Trades"])


# --------------------------------------------------
# EXECUTE TRADE
# --------------------------------------------------
@router.post("/trade-plans/{plan_id}/execute")
def execute_trade(plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(models.TradePlan, plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Trade plan not found")

    if plan.plan_status != models.PlanStatus.PLANNED:
        raise HTTPException(
            status_code=409,
            detail=f"Trade plan not executable (status={plan.plan_status})"
        )

    trade = models.TradeLog(
        # REQUIRED FIELDS
        timestamp=datetime.utcnow(),

        # ✅ FIX 1: symbol comes from plan
        symbol=plan.symbol,

        side=models.TradeSide.BUY
        if plan.position_type == "LONG"
        else models.TradeSide.SELL,

        quantity=plan.planned_position_size,
        price=plan.planned_entry_price,

        # OPTIONAL / CONTROLLED FIELDS
        entry_price=plan.planned_entry_price,
        strategy=plan.strategy,
        position_type=models.PositionType(plan.position_type),

        # ENUM SAFE
        source=models.TradeSource.manual,
        status=models.TradeStatus.filled,
    )

    db.add(trade)
    db.flush()  # get trade.id

    plan.trade_id = trade.id
    plan.plan_status = models.PlanStatus.EXECUTED

    db.commit()

    return {
        "trade_id": trade.id,
        "status": "EXECUTED",
    }


# --------------------------------------------------
# EXIT TRADE
# --------------------------------------------------
@router.post("/trades/{trade_id}/exit")
def exit_trade(
    trade_id: int,
    payload: schemas.ExitTradePayload,
    db: Session = Depends(get_db)
):
    trade = db.get(models.TradeLog, trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")

    if trade.exit_timestamp:
        raise HTTPException(409, "Trade already exited")

    trade.exit_price = payload.exit_price
    trade.exit_reason = payload.exit_reason
    trade.exit_timestamp = payload.exit_timestamp

    db.commit()

    return {"status": "EXITED"}


# --------------------------------------------------
# REVIEW TRADE
# --------------------------------------------------
@router.post("/trades/{trade_id}/review")
def submit_review(
    trade_id: int,
    payload: schemas.TradeReviewPayload,
    db: Session = Depends(get_db)
):
    trade = db.get(models.TradeLog, trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")

    if not trade.exit_timestamp:
        raise HTTPException(400, "Trade not exited")

    existing = (
        db.query(models.TradeExecutionReview)
        .filter_by(trade_id=trade_id)
        .first()
    )
    if existing:
        raise HTTPException(409, "Review already exists")

    review = models.TradeExecutionReview(
        trade_id=trade_id,

        # ✅ FIX 2: freeze symbol from executed trade
        symbol=trade.symbol,

        exit_reason=payload.exit_reason,
        followed_entry_rules=payload.followed_entry_rules,
        followed_stop_rules=payload.followed_stop_rules,
        followed_position_sizing=payload.followed_position_sizing,
        emotional_state=payload.emotional_state,
        market_context=payload.market_context,
        learning_insight=payload.learning_insight,
        trade_grade=payload.trade_grade,
    )

    db.add(review)
    db.commit()

    return {"status": "REVIEWED"}
