# backend/app/api/step4.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.step4_schema import (
    Step4FreezeRequest,
    Step4FrozenTradeResponse,
)
from backend.app.services.step4_service import freeze_step4_trade

router = APIRouter(prefix="/api/step4", tags=["STEP-4"])


@router.post(
    "/freeze",
    response_model=Step4FrozenTradeResponse,
)
def freeze_trade(
    request: Step4FreezeRequest,
    db: Session = Depends(get_db),
):
    """
    Freeze final trade execution intent (irreversible).
    """
    try:
        return freeze_step4_trade(
            db=db,
            request=request,
        )
    except ValueError as e:
        # Domain rule violations (most common)
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))