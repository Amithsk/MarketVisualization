#backend/app/api/step1.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from backend.app.db.session import get_db
from backend.app.schemas.step1_schema import (
    Step1PreviewRequest,
    Step1FreezeRequest,
    Step1ComputeRequest,
    Step1PreviewResponse,
    Step1FrozenResponse,
    Step1ComputeResponse,
)
from backend.app.services.step1_service import (
    preview_step1_context,
    freeze_step1_context,
    compute_step1_context,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step1",
    tags=["STEP-1"],
)


@router.post(
    "/preview",
    response_model=Step1PreviewResponse,
    status_code=status.HTTP_200_OK,
)
def preview_step1(
    request: Step1PreviewRequest,
    db: Session = Depends(get_db),
):
    """
    STEP-1 Preview — Pre-Market Context
    """
    try:
        return preview_step1_context(
            db=db,
            trade_date=request.trade_date,
        )

    except Exception:
        logger.exception(
            "[STEP-1][API][PREVIEW] unhandled exception"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate STEP-1 preview",
        )


@router.post(
    "/compute",
    response_model=Step1ComputeResponse,
    status_code=status.HTTP_200_OK,
)
def compute_step1(
    request: Step1ComputeRequest,
):
    """
    STEP-1 Compute — MANUAL MODE ONLY
    """
    try:
        return compute_step1_context(request)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception:
        logger.exception(
            "[STEP-1][API][COMPUTE] unhandled exception"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute STEP-1 context",
        )


@router.post(
    "/freeze",
    response_model=Step1FrozenResponse,
    status_code=status.HTTP_200_OK,
)
def freeze_step1(
    request: Step1FreezeRequest,
    db: Session = Depends(get_db),
):
    """
    STEP-1 Freeze — Irreversible
    AUTHORITATIVE SNAPSHOT
    """
    try:
        return freeze_step1_context(
            db=db,
            trade_date=request.trade_date,
            preopen_price=request.preopen_price,
            derived_context=request.derived_context,
            market_bias=request.market_bias,
            gap_context=request.gap_context,
            premarket_notes=request.premarket_notes,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception:
        logger.exception(
            "[STEP-1][API][FREEZE] unhandled exception"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to freeze STEP-1 context",
        )
