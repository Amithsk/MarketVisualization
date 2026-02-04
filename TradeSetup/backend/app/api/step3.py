# backend/app/api/step3.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.step3_schema import Step3ExecutionResponse
from backend.app.services.step3_service import generate_step3_execution
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/api/step3", tags=["STEP-3"])


class Step3ExecuteRequest(BaseModel):
    trade_date: date


@router.post(
    "/execute",
    response_model=Step3ExecutionResponse,
)
def execute_step3(
    request: Step3ExecuteRequest,
    db: Session = Depends(get_db),
):
    """
    Generate STEP-3 execution control & stock selection.
    Read-only and deterministic.
    """
    try:
        return generate_step3_execution(
            db=db,
            trade_date=request.trade_date,
        )
    except ValueError as e:
        # STEP-1 or STEP-2 not frozen
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))