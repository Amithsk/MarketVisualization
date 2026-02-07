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


class Step3ExecuteRequest(BaseModel):
    """
    STEP-3 execution request.

    System-triggered.
    No trader discretion.
    """
    trade_date: date = Field(
        ...,
        description="Trading date for STEP-3 execution"
    )


@router.post(
    "/execute",
    response_model=Step3ExecutionResponse,
    status_code=status.HTTP_200_OK,
)
def execute_step3(
    request: Step3ExecuteRequest,
    db: Session = Depends(get_db),
):
    """
    STEP-3 — Execution Control & Candidate Selection

    - Deterministic
    - Idempotent
    - Backend-authoritative
    - Never fails due to missing automation
    """

    try:
        return generate_step3_execution(
            db=db,
            trade_date=request.trade_date,
        )

    except ValueError as e:
        # Domain violation (STEP-1 / STEP-2 not frozen)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        # Infrastructure / unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute STEP-3",
        )
