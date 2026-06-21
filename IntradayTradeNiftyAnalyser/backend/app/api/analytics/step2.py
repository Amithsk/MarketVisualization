#IntradayTradeNiftyAnalyser/backend/app/api/analytics/step2.py

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db

from backend.app.services.analytics.step2_service import (
    Step2Service,
)

from backend.app.schemas.analytics.step2 import (
    Step2ResponseSchema,
)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get(
    "/step2/{trade_date}",
    response_model=Step2ResponseSchema,
)
def get_step2_validation(
    trade_date: str,
    db: Session = Depends(get_db),
):
    """
    ====================================================
    STEP 2 VALIDATION

    Purpose:
        Returns STEP 2 system output and
        market validation output.

    UI Section:
        STEP 2 VALIDATION

    Example:
        /api/analytics/step2/2026-06-11
    ====================================================
    """

    service = Step2Service(db)

    return service.get_step2_validation(
        trade_date
    )