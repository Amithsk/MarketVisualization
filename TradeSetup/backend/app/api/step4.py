# backend/app/api/step4.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import traceback
import logging

from backend.app.db.session import get_db
from backend.app.schemas.step4_schema import (
    Step4PreviewRequest,
    Step4PreviewResponse,
    Step4ComputeRequest,
    Step4ComputeResponse,
    Step4FreezeRequest,
    Step4FrozenTradeResponse,
)
from backend.app.services.step4_service import (
    load_step4_context,
    compute_step4_trade,
    freeze_step4_trade,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step4",
    tags=["STEP-4"],
)


# =====================================================
# STEP-4 PREVIEW (PHASE-1: CONTEXT LOAD)
# =====================================================

@router.post(
    "/preview",
    response_model=Step4PreviewResponse,
    status_code=status.HTTP_200_OK,
)
def preview_trade(
    request: Step4PreviewRequest,
    db: Session = Depends(get_db),
):
    """
    STEP-4 Phase-1:
    Load structural execution blueprint from STEP-3.
    No risk calculation happens here.
    """

    logger.info(
        "[STEP4][API][PREVIEW][START] trade_date=%s",
        request.trade_date,
    )

    try:
        response = load_step4_context(
            db=db,
            trade_date=request.trade_date,
        )

        logger.info(
            "[STEP4][API][PREVIEW][SUCCESS] trade_date=%s mode=%s candidates=%d",
            request.trade_date,
            response.mode,
            len(response.candidates),
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        logger.error("[STEP4][PREVIEW][UNEXPECTED ERROR]")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# =====================================================
# STEP-4 COMPUTE (PHASE-2)
# =====================================================

@router.post(
    "/compute",
    response_model=Step4ComputeResponse,
    status_code=status.HTTP_200_OK,
)
def compute_trade(
    request: Step4ComputeRequest,
    db: Session = Depends(get_db),
):
    """
    STEP-4 Phase-2:
    Perform deterministic execution math and upsert construction.
    """

    logger.info(
        "[STEP4][API][COMPUTE][START] trade_date=%s symbol=%s",
        request.trade_date,
        request.symbol,
    )

    try:
        response = compute_step4_trade(
            db=db,
            request=request,
        )

        logger.info(
            "[STEP4][API][COMPUTE][SUCCESS] trade_date=%s symbol=%s status=%s",
            request.trade_date,
            request.symbol,
            response.preview.trade_status,
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        logger.error("[STEP4][COMPUTE][UNEXPECTED ERROR]")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# =====================================================
# STEP-4 FREEZE
# =====================================================

@router.post(
    "/freeze",
    response_model=Step4FrozenTradeResponse,
    status_code=status.HTTP_200_OK,
)
def freeze_trade(
    request: Step4FreezeRequest,
    db: Session = Depends(get_db),
):
    """
    Freeze final trade execution intent (irreversible).
    """

    logger.info(
        "[STEP4][API][FREEZE][START] trade_date=%s symbol=%s",
        request.trade_date,
        request.symbol,
    )

    try:
        response = freeze_step4_trade(
            db=db,
            request=request,
        )

        logger.info(
            "[STEP4][API][FREEZE][SUCCESS] trade_date=%s symbol=%s",
            request.trade_date,
            request.symbol,
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        logger.error("[STEP4][FREEZE][UNEXPECTED ERROR]")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )