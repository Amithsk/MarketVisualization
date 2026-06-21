#IntradayTradeNiftyAnalyser/backend/app/api/analytics/performance.py
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db

from backend.app.services.analytics.performance_service import (
    PerformanceService,
)

from backend.app.schemas.analytics.performance import (
    PerformanceResponseSchema,
)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get(
    "/performance/{trade_date}",
    response_model=PerformanceResponseSchema,
)
def get_performance(
    trade_date: str,
    db: Session = Depends(get_db),
):
    """
    ====================================================
    STEP 3 PERFORMANCE

    Purpose:
        Returns STEP 3 execution information
        and performance metrics.

    UI Sections:
        STEP 3 PERFORMANCE

    Example:
        /api/analytics/performance/2026-06-11
    ====================================================
    """

    service = PerformanceService(db)

    return service.get_performance(
        trade_date
    )