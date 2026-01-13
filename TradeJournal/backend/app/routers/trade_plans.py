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
