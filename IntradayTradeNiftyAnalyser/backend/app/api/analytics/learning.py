#IntradayTradeNiftyAnalyser/backend/app/api/analytics/learning.py
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db

from backend.app.services.analytics.learning_service import (
    LearningService,
)

from backend.app.schemas.analytics.learning import (
    LearningResponseSchema,
)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get(
    "/learning/{trade_date}",
    response_model=LearningResponseSchema,
)
def get_learning(
    trade_date: str,
    db: Session = Depends(get_db),
):
    """
    ====================================================
    LEARNING SUMMARY

    Purpose:
        Returns analytical engine learning output.

    UI Sections:
        WHAT DID I LEARN TODAY?
        IMPROVEMENT TRACKER

    Example:
        /api/analytics/learning/2026-06-11
    ====================================================
    """

    service = LearningService(db)

    return service.get_learning(
        trade_date
    )