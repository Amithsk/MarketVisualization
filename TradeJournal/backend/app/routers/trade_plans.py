#/TradeJournal/backend/app/routers/trade_plans.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db

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
        })

    return enriched_plans