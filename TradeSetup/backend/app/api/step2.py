# backend/app/api/step2.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import traceback

from backend.app.db.session import get_db
from backend.app.schemas.step2_schema import (
    Step2PreviewRequest,
    Step2FreezeRequest,
    Step2ComputeRequest,
    Step2PreviewResponse,
    Step2FrozenResponse,
    Step2ComputeResponse,
)
from backend.app.services.step2_service import (
    preview_step2_behavior,
    freeze_step2_behavior,
    compute_step2_behavior,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step2",
    tags=["STEP-2"],
)

# =====================================================
# PREVIEW
# =====================================================

@router.post(
    "/preview",
    response_model=Step2PreviewResponse,
    status_code=status.HTTP_200_OK,
)
def preview_step2(
    request: Step2PreviewRequest,
    db: Session = Depends(get_db),
):

    logger.info(
        "[STEP2][API][PREVIEW][START] trade_date=%s",
        request.trade_date,
    )

    try:
        result = preview_step2_behavior(
            db=db,
            trade_date=request.trade_date,
        )

        logger.info(
            "[STEP2][API][PREVIEW][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return result

    except ValueError as e:

        logger.warning(
            "[STEP2][API][PREVIEW][DOMAIN_ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:

        logger.error(
            "[STEP2][API][PREVIEW][FATAL] trade_date=%s exception=%s",
            request.trade_date,
            str(e),
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate STEP-2 preview",
        )


# =====================================================
# COMPUTE
# =====================================================

@router.post(
    "/compute",
    response_model=Step2ComputeResponse,
    status_code=status.HTTP_200_OK,
)
def compute_step2(
    request: Step2ComputeRequest,
    db: Session = Depends(get_db),
):

    logger.info(
        "[STEP2][API][COMPUTE][START] trade_date=%s candles=%s",
        request.trade_date,
        len(request.candles),
    )

    try:
        result = compute_step2_behavior(
            db=db,
            trade_date=request.trade_date,
            candles=request.candles,
            avg_5m_range_prev_day=request.avg_5m_range_prev_day,
        )

        logger.info(
            "[STEP2][API][COMPUTE][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return result

    except ValueError as e:

        logger.warning(
            "[STEP2][API][COMPUTE][DOMAIN_ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:

        logger.error(
            "[STEP2][API][COMPUTE][FATAL] trade_date=%s exception=%s",
            request.trade_date,
            str(e),
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute STEP-2 behavior",
        )


# =====================================================
# FREEZE
# =====================================================

@router.post(
    "/freeze",
    response_model=Step2FrozenResponse,
    status_code=status.HTTP_200_OK,
)
def freeze_step2(
    request: Step2FreezeRequest,
    db: Session = Depends(get_db),
):

    logger.info(
        "[STEP2][API][FREEZE][START] trade_date=%s candles=%s",
        request.trade_date,
        len(request.candles),
    )

    try:
        result = freeze_step2_behavior(
            db=db,
            trade_date=request.trade_date,
            candles=request.candles,
            reason=request.reason,  # baseline removed (correct)
        )

        logger.info(
            "[STEP2][API][FREEZE][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return result

    except ValueError as e:

        logger.warning(
            "[STEP2][API][FREEZE][DOMAIN_ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:

        logger.error(
            "[STEP2][API][FREEZE][FATAL] trade_date=%s exception=%s",
            request.trade_date,
            str(e),
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to freeze STEP-2 behavior",
        )