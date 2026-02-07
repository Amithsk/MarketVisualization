#backend/app/api/step3.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.schemas.step3_schema import Step3ExecutionResponse
from backend.app.services.step3_service import generate_step3_execution

router = APIRouter(
    prefix="/api/step3",
    tags=["STEP-3"],
)


class Step3ExecuteRequest(BaseModel):
    """
    Execution request for STEP-3.
    System-driven, no user discretion.
    """
    trade_date: date


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
    Generate STEP-3 execution control & stock selection.

    Deterministic.
    Idempotent.
    Irreversible once generated.
    """
    try:
        return generate_step3_execution(
            db=db,
            trade_date=request.trade_date,
        )
    except ValueError as e:
        # Domain error: STEP-1 / STEP-2 not frozen
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception:
        # Infrastructure / unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate STEP-3 execution control",
        )
