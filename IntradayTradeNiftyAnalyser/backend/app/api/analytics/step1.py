#IntradayTradeNiftyAnalyser/backend/app/api/analytics/step1.py

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db

from backend.app.services.analytics.step1_service import (
    Step1Service,
)

from backend.app.schemas.analytics.step1 import (
    Step1ResponseSchema,
)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get(
    "/step1/{trade_date}",
    response_model=Step1ResponseSchema,
)
def get_step1_validation(
    trade_date: str,
    db: Session = Depends(get_db),
):
    """
    ====================================================
    STEP 1 VALIDATION

    Purpose:
        Returns STEP 1 system output and
        market validation output.

    UI Section:
        STEP 1 VALIDATION

    Example:
        /api/analytics/step1/2026-06-11
    ====================================================
    """

    service = Step1Service(db)

    return service.get_step1_validation(
        trade_date
    )