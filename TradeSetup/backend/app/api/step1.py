# backend/app/api/step1.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.step1_schema import (
    Step1PreviewRequest,
    Step1FreezeRequest,
    Step1PreviewResponse,
    Step1FrozenResponse,
)
from backend.app.services.step1_service import (
    preview_step1_context,
    freeze_step1_context,
)

router = APIRouter(prefix="/api/step1", tags=["STEP-1"])


@router.post(
    "/preview",
    response_model=Step1PreviewResponse,
)
def preview_step1(
    request: Step1PreviewRequest,
    db: Session = Depends(get_db),
):
    """
    Preview STEP-1 pre-market context (read-only).
    """
    try:
        return preview_step1_context(
            db=db,
            trade_date=request.trade_date,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/freeze",
    response_model=Step1FrozenResponse,
)
def freeze_step1(
    request: Step1FreezeRequest,
    db: Session = Depends(get_db),
):
    """
    Freeze STEP-1 context (irreversible).
    """
    try:
        return freeze_step1_context(
            db=db,
            trade_date=request.trade_date,
            market_bias=request.market_bias,
            premarket_notes=request.premarket_notes,
        )
    except ValueError as e:
        # Domain error (already frozen, etc.)
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))