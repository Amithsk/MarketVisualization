# backend/app/api/step2.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.step2_schema import (
    Step2PreviewRequest,
    Step2FreezeRequest,
    Step2PreviewResponse,
    Step2FrozenResponse,
)
from backend.app.services.step2_service import (
    preview_step2_behavior,
    freeze_step2_behavior,
)

router = APIRouter(prefix="/api/step2", tags=["STEP-2"])


@router.post(
    "/preview",
    response_model=Step2PreviewResponse,
)
def preview_step2(
    request: Step2PreviewRequest,
    db: Session = Depends(get_db),
):
    """
    Preview STEP-2 market open behavior (read-only).
    """
    try:
        return preview_step2_behavior(
            db=db,
            trade_date=request.trade_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/freeze",
    response_model=Step2FrozenResponse,
)
def freeze_step2(
    request: Step2FreezeRequest,
    db: Session = Depends(get_db),
):
    """
    Freeze STEP-2 market open behavior (irreversible).
    """
    try:
        return freeze_step2_behavior(
            db=db,
            trade_date=request.trade_date,
            index_open_behavior=request.index_open_behavior,
            early_volatility=request.early_volatility,
            market_participation=request.market_participation,
            trade_allowed=request.trade_allowed,
        )
    except ValueError as e:
        # STEP-1 not frozen, STEP-2 already frozen, etc.
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))