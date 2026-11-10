# TradeJournal/backend/app/routers/trades.py

from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db
from app.market_time import MARKET_TIMEZONE, to_api_time, to_market_time, to_storage_time

router = APIRouter(prefix="/api", tags=["Trades"])


def _decimal(value) -> Decimal:
    return Decimal(str(value))


def _opening_side(trade):
    return models.TradeSide.BUY if trade.position_type == models.PositionType.LONG else models.TradeSide.SELL


def _exit_side(trade):
    return models.TradeSide.SELL if _opening_side(trade) == models.TradeSide.BUY else models.TradeSide.BUY


def _execution_response(row):
    return {"id": row.id, "sequence": row.sequence, "event_type": row.event_type,
            "side": row.side.value if hasattr(row.side, "value") else row.side,
            "quantity": row.quantity, "price": float(row.price),
            "execution_timestamp": to_api_time(row.execution_timestamp), "reason": row.reason,
            "note": row.note}


def _duplicate(db, trade_id, request_id):
    if not request_id:
        return None
    return db.query(models.TradeExecution).filter_by(
        trade_id=trade_id, client_request_id=request_id).first()


def _latest_execution(trade):
    return trade.executions[-1] if trade.executions else None


def _assert_event_time(trade, timestamp):
    latest = _latest_execution(trade)
    if latest and timestamp < latest.execution_timestamp:
        raise HTTPException(422, "Execution timestamp cannot be earlier than the latest execution")


def _append_execution(trade, event_type, side, quantity, price, timestamp, reason=None, note=None, request_id=None):
    row = models.TradeExecution(sequence=len(trade.executions) + 1, event_type=event_type,
        side=side, quantity=quantity, price=price, execution_timestamp=timestamp,
        reason=reason, note=note, client_request_id=request_id)
    trade.executions.append(row)
    return row


# --------------------------------------------------
# EXECUTE TRADE
# --------------------------------------------------
@router.post("/trade-plans/{plan_id}/execute")
def execute_trade(plan_id: int,
                  payload: schemas.ExecuteTradePayload,
                  db: Session = Depends(get_db)
                  ):
    plan = db.query(models.TradePlan).filter_by(id=plan_id).with_for_update().first()

    if not plan:
        raise HTTPException(status_code=404, detail="Trade plan not found")

    if plan.plan_status != models.PlanStatus.PLANNED:
        if plan.trade_id and payload.client_request_id:
            existing = _duplicate(db, plan.trade_id, payload.client_request_id)
            if existing:
                return {"trade_id": plan.trade_id, "status": "DUPLICATE",
                        "entry_timestamp": to_api_time(existing.execution_timestamp)}
        raise HTTPException(
            status_code=409,
            detail=f"Trade plan not executable (status={plan.plan_status})"
        )
    trade_timestamp = to_storage_time(
        payload.entry_timestamp
        if payload.entry_timestamp
        else datetime.now(MARKET_TIMEZONE)
    )

    quantity = payload.quantity or plan.planned_position_size
    price = _decimal(payload.price if payload.price is not None else plan.planned_entry_price)
    if quantity <= 0 or price <= 0:
        raise HTTPException(422, "Quantity and price must be positive")
    opening_side = models.TradeSide.BUY if plan.position_type == "LONG" else models.TradeSide.SELL
    trade = models.TradeLog(
        # REQUIRED FIELDS
        timestamp=trade_timestamp,

        # ✅ FIX 1: symbol comes from plan
        symbol=plan.symbol,

        side=opening_side,

        quantity=quantity,
        price=price,

        # OPTIONAL / CONTROLLED FIELDS
        entry_price=price,
        strategy=plan.strategy,
        position_type=models.PositionType(plan.position_type),

        # ENUM SAFE
        source=models.TradeSource.manual,
        status=models.TradeStatus.filled,
        is_phase1_position=1,
        open_quantity=quantity,
        total_entered_quantity=quantity,
        remaining_avg_entry_price=price,
        realized_gross_pnl=Decimal("0"),
        total_entry_notional=price * quantity,
    )

    db.add(trade)
    db.flush()  # get trade.id

    _append_execution(trade, "ENTRY", opening_side, quantity, price, trade_timestamp,
                      request_id=payload.client_request_id)
    plan.trade_id = trade.id
    plan.plan_status = models.PlanStatus.EXECUTED

    db.commit()

    return {
        "trade_id": trade.id,
        "status": "EXECUTED",
        "entry_timestamp": to_api_time(trade.timestamp),
    }


@router.post("/trades/{trade_id}/add")
def add_to_position(trade_id: int, payload: schemas.AddTradePayload, db: Session = Depends(get_db)):
    # Lock serializes Add/Exit calculations for a position.
    trade = db.query(models.TradeLog).filter_by(id=trade_id).with_for_update().first()
    if not trade:
        raise HTTPException(404, "Trade not found")
    existing = _duplicate(db, trade_id, payload.client_request_id)
    if existing:
        return {"status": "DUPLICATE", "execution": _execution_response(existing)}
    if not trade.is_phase1_position:
        raise HTTPException(409, "Legacy positions do not support adds")
    if trade.open_quantity == 0:
        raise HTTPException(409, "Trade already closed")
    timestamp = to_storage_time(payload.execution_timestamp)
    _assert_event_time(trade, timestamp)
    price = _decimal(payload.price)
    old_value = _decimal(trade.remaining_avg_entry_price) * trade.open_quantity
    trade.open_quantity += payload.quantity
    trade.total_entered_quantity += payload.quantity
    trade.total_entry_notional = _decimal(trade.total_entry_notional) + price * payload.quantity
    trade.quantity = trade.total_entered_quantity  # Replay-compatible final position size.
    trade.remaining_avg_entry_price = (old_value + price * payload.quantity) / trade.open_quantity
    row = _append_execution(trade, "ADD", _opening_side(trade), payload.quantity, price, timestamp,
                            note=payload.note, request_id=payload.client_request_id)
    db.commit()
    db.refresh(row)
    return {"status": "ADDED", "execution": _execution_response(row), "open_quantity": trade.open_quantity,
            "remaining_avg_entry_price": float(trade.remaining_avg_entry_price),
            "realized_gross_pnl": float(trade.realized_gross_pnl)}


# --------------------------------------------------
# EXIT TRADE
# --------------------------------------------------
@router.post("/trades/{trade_id}/exit")
def exit_trade(
    trade_id: int,
    payload: schemas.ExitTradePayload,
    db: Session = Depends(get_db)
):
    trade = db.query(models.TradeLog).filter_by(id=trade_id).with_for_update().first()
    if not trade:
        raise HTTPException(404, "Trade not found")

    if trade.exit_timestamp:
        raise HTTPException(409, "Trade already exited")

    # Retain the legacy one-shot full-exit path for pre-Phase-1 rows.
    if not trade.is_phase1_position:
        if payload.quantity is not None:
            raise HTTPException(409, "Legacy positions only support a full exit")
        exit_timestamp = to_storage_time(payload.exit_timestamp)
        entry_timestamp = to_market_time(trade.timestamp)
        if exit_timestamp < entry_timestamp.replace(tzinfo=None):
            raise HTTPException(422, "Exit timestamp cannot be earlier than entry timestamp")
        trade.exit_price = payload.exit_price
        trade.exit_reason = payload.exit_reason
        trade.exit_timestamp = exit_timestamp
        db.commit()
        return {"status": "EXITED", "exit_timestamp": to_api_time(trade.exit_timestamp)}

    existing = _duplicate(db, trade_id, payload.client_request_id)
    if existing:
        return {"status": "DUPLICATE", "execution": _execution_response(existing)}
    if trade.open_quantity == 0:
        raise HTTPException(409, "Trade already closed")
    exit_timestamp = to_storage_time(payload.exit_timestamp)
    _assert_event_time(trade, exit_timestamp)
    quantity = payload.quantity if payload.quantity is not None else trade.open_quantity
    if quantity > trade.open_quantity:
        raise HTTPException(422, "Exit quantity cannot exceed open quantity")
    price = _decimal(payload.exit_price)
    average = _decimal(trade.remaining_avg_entry_price)
    per_share = price - average if _opening_side(trade) == models.TradeSide.BUY else average - price
    trade.realized_gross_pnl = _decimal(trade.realized_gross_pnl) + per_share * quantity
    trade.open_quantity -= quantity
    row = _append_execution(trade, "EXIT", _exit_side(trade), quantity, price, exit_timestamp,
                            reason=payload.exit_reason, request_id=payload.client_request_id)
    if trade.open_quantity == 0:
        trade.exit_price = price
        trade.exit_reason = payload.exit_reason
        trade.exit_timestamp = exit_timestamp
        trade.realized_gross_pnl_pct = (trade.realized_gross_pnl / trade.total_entry_notional) * Decimal("100") if trade.total_entry_notional else None
    db.commit()
    db.refresh(row)
    return {"status": "EXITED" if trade.open_quantity == 0 else "PARTIALLY_EXITED",
            "execution": _execution_response(row), "open_quantity": trade.open_quantity,
            "remaining_avg_entry_price": float(trade.remaining_avg_entry_price),
            "realized_gross_pnl": float(trade.realized_gross_pnl),
            "realized_gross_pnl_pct": float(trade.realized_gross_pnl_pct) if trade.realized_gross_pnl_pct is not None else None,
            "exit_timestamp": to_api_time(trade.exit_timestamp)}


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
