# backend/app/api/step3.py

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging
import traceback

from backend.app.db.session import get_db
from backend.app.schemas.step3_schema import Step3ExecutionResponse
from backend.app.services.step3_service import generate_step3_execution

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step3",
    tags=["STEP-3"],
)


class Step3PreviewRequest(BaseModel):
    trade_date: date = Field(...)


@router.post(
    "/preview",
    response_model=Step3ExecutionResponse,
    status_code=status.HTTP_200_OK,
)
def preview_step3(
    request: Step3PreviewRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        "[STEP3][API][PREVIEW][START] trade_date=%s",
        request.trade_date,
    )

    try:
        response = generate_step3_execution(
            db=db,
            trade_date=request.trade_date,
        )

        logger.info(
            "[STEP3][API][PREVIEW][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return response

    except ValueError as e:
        logger.error(
            "[STEP3][API][DOMAIN_ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "[STEP3][API][UNEXPECTED_ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
