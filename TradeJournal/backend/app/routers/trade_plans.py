#/TradeJournal/backend/app/routers/trade_plans.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db
from app.market_time import to_api_time

router = APIRouter(prefix="/api/trade-plans", tags=["Trade Plans"])


@router.post("")
def create_plan(
    payload: schemas.TradePlanCreate,
    db: Session = Depends(get_db)
):
    plan = models.TradePlan(
        # ✅ NEW — persist symbol at plan level
        symbol=payload.symbol,

        plan_date=payload.plan_date,
        trade_mode=payload.trade_mode,
        strategy=payload.strategy,
        position_type=payload.position_type,
        setup_description=payload.setup_description,
        planned_entry_price=payload.planned_entry_price,
        planned_stop_price=payload.planned_stop_price,
        planned_target_price=payload.planned_target_price,
        planned_risk_amount=payload.planned_risk_amount,
        planned_position_size=payload.planned_position_size,
        plan_status=models.PlanStatus.PLANNED,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {"plan_id": plan.id}


@router.post("/{plan_id}/not-taken")
def mark_not_taken(
    plan_id: int,
    payload: schemas.NotTakenPayload,
    db: Session = Depends(get_db)
):
    plan = db.get(models.TradePlan, plan_id)
    if not plan:
        raise HTTPException(404, "Trade plan not found")

    if plan.plan_status != models.PlanStatus.PLANNED:
        raise HTTPException(409, "Only PLANNED trades can be marked NOT_TAKEN")

    plan.plan_status = models.PlanStatus.NOT_TAKEN
    plan.not_taken_reason = payload.not_taken_reason

    db.commit()

    return {"status": "NOT_TAKEN"}


# --------------------------------------------------
# LIST PLANS WITH TRADE STATE
# --------------------------------------------------

@router.get("")
def list_plans(
    trade_date: str,
    db: Session = Depends(get_db)
):
    plans = (
        db.query(models.TradePlan)
        .filter(models.TradePlan.plan_date == trade_date)
        .order_by(models.TradePlan.id.asc())
        .all()
    )

    enriched_plans = []

    for plan in plans:

        # --------------------------------------------------
        # TRADE EXECUTION STATE
        # --------------------------------------------------

        is_executed = plan.trade_id is not None

        is_exited = False
        is_reviewed = False

        # --------------------------------------------------
        # CHECK EXIT + REVIEW STATE
        # --------------------------------------------------

        if plan.trade:

            # EXITED?
            is_exited = plan.trade.exit_timestamp is not None

            # REVIEWED?
            review_exists = (
                db.query(models.TradeExecutionReview)
                .filter(
                    models.TradeExecutionReview.trade_id == plan.trade.id
                )
                .first()
            )

            is_reviewed = review_exists is not None

        position = None
        executions = []
        if plan.trade:
            position = {
                "open_quantity": plan.trade.open_quantity,
                "total_entered_quantity": plan.trade.total_entered_quantity,
                "remaining_avg_entry_price": float(plan.trade.remaining_avg_entry_price) if plan.trade.remaining_avg_entry_price is not None else None,
                "realized_gross_pnl": float(plan.trade.realized_gross_pnl) if plan.trade.realized_gross_pnl is not None else None,
                "realized_gross_pnl_pct": float(plan.trade.realized_gross_pnl_pct) if plan.trade.realized_gross_pnl_pct is not None else None,
                "is_phase1_position": bool(plan.trade.is_phase1_position),
            }
            executions = [{
                "id": item.id, "sequence": item.sequence, "event_type": item.event_type,
                "side": item.side.value if hasattr(item.side, "value") else item.side,
                "quantity": item.quantity, "price": float(item.price),
                "execution_timestamp": to_api_time(item.execution_timestamp), "reason": item.reason,
                "note": item.note,
            } for item in plan.trade.executions]

        # --------------------------------------------------
        # ENRICHED RESPONSE
        # --------------------------------------------------

        enriched_plans.append({
            "id": plan.id,
            "trade_id": plan.trade_id,

            "symbol": plan.symbol,

            "plan_date": plan.plan_date,
            "trade_mode": plan.trade_mode,
            "strategy": plan.strategy,
            "position_type": plan.position_type,

            "setup_description": plan.setup_description,
            "entry_trigger": plan.entry_trigger,

            "planned_entry_price": plan.planned_entry_price,
            "planned_stop_price": plan.planned_stop_price,
            "planned_target_price": plan.planned_target_price,

            "planned_risk_amount": plan.planned_risk_amount,
            "planned_position_size": plan.planned_position_size,

            "plan_status": plan.plan_status.value,

            "not_taken_reason": plan.not_taken_reason,

            "created_at": plan.created_at,
            "updated_at": plan.updated_at,

            # ✅ NEW
            "trade_state": {
                "is_executed": is_executed,
                "is_exited": is_exited,
                "is_reviewed": is_reviewed,
            }
            ,"position": position,
            "executions": executions,
        })

    return enriched_plans
