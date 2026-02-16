# backend/app/api/step3.py

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.app.db.session import get_db
from backend.app.schemas.step3_schema import Step3ExecutionResponse
from backend.app.services.step3_service import generate_step3_execution

router = APIRouter(
    prefix="/api/step3",
    tags=["STEP-3"],
)


class Step3PreviewRequest(BaseModel):
    """
    STEP-3 preview request.

    System-triggered.
    No trader discretion.
    """
    trade_date: date = Field(
        ...,
        description="Trading date for STEP-3 preview"
    )


@router.post(
    "/preview",
    response_model=Step3ExecutionResponse,
    status_code=status.HTTP_200_OK,
)
def preview_step3(
    request: Step3PreviewRequest,
    db: Session = Depends(get_db),
):
    """
    STEP-3 — Execution Control & Stock Selection

    LOCKED RULES:
    - Backend is source of truth
    - STEP-3A always computed
    - STEP-3B always activated after STEP-1 & STEP-2 freeze
    - Never fails due to missing automation
    - Idempotent
    """

    try:
        return generate_step3_execution(
            db=db,
            trade_date=request.trade_date,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview STEP-3",
        )
