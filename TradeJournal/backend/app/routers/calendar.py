# backend/app/routers/calendar.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

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
            cast(models.TradeLog.timestamp, Date).label("trade_date"),
            func.count(models.TradeLog.id).label("trade_count"),
            func.coalesce(func.sum(models.TradeLog.pnl_amount), 0).label("pnl"),
        )
        .filter(func.year(models.TradeLog.timestamp) == year)
        .filter(func.month(models.TradeLog.timestamp) == month)
        .group_by(cast(models.TradeLog.timestamp, Date))
        .all()
    )

    summary = {}

    for row in results:
        summary[str(row.trade_date)] = {
            "tradeCount": int(row.trade_count),
            "pnl": float(row.pnl),
        }

    return summary
