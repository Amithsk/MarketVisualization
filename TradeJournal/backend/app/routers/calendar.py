# backend/app/routers/calendar.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, case

from app import models
from app.deps import get_db

router = APIRouter(
    prefix="/api/calendar",
    tags=["Calendar"]
)


@router.get("/summary")
def get_calendar_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """
    Returns per-day trade summary for a given month.

    Response shape:
    {
      "YYYY-MM-DD": {
        "tradeCount": int,
        "pnl": float
      }
    }
    """

    results = (
         db.query(
        models.TradePlan.plan_date.label("trade_date"),

        func.count(models.TradePlan.id).label("trade_count"),

        func.coalesce(func.sum(
            # Phase-1 positions report only their final accumulated result.
            # Legacy rows retain the deployed generated-column calculation.
            case(
                (models.TradeLog.is_phase1_position == 1,
                 case((models.TradeLog.open_quantity == 0,
                       models.TradeLog.realized_gross_pnl - func.coalesce(models.TradeLog.fees, 0)), else_=0)),
                else_=models.TradeLog.pnl_amount,
            )
        ), 0).label("pnl"),
    )

    # --------------------------------------------------
    # JOIN trade_log (optional)
    # because PLANNED trades may not have trade_id yet
    # --------------------------------------------------
    .outerjoin(
        models.TradeLog,
        models.TradePlan.trade_id == models.TradeLog.id
    )

    # --------------------------------------------------
    # BUSINESS DATE FILTERING
    # IMPORTANT:
    # Use plan_date ONLY
    # --------------------------------------------------
    .filter(func.year(models.TradePlan.plan_date) == year)

    .filter(func.month(models.TradePlan.plan_date) == month)

    # --------------------------------------------------
    # GROUP BY BUSINESS DATE
    # --------------------------------------------------
    .group_by(models.TradePlan.plan_date)

    .all()
    )

    summary = {}

    for row in results:
        summary[str(row.trade_date)] = {
            "tradeCount": int(row.trade_count),
            "pnl": float(row.pnl),
        }

    return summary
