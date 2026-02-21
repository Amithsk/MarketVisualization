# backend/app/api/step4.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import traceback
import logging

from backend.app.db.session import get_db
from backend.app.schemas.step4_schema import (
    Step4PreviewRequest,
    Step4PreviewResponse,
    Step4FreezeRequest,
    Step4FrozenTradeResponse,
)
from backend.app.services.step4_service import (
    preview_step4_trade,
    freeze_step4_trade,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step4",
    tags=["STEP-4"],
)


# =====================================================
# STEP-4 PREVIEW
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
    Generate / overwrite STEP-4 construction snapshot.
    """

    try:
        return preview_step4_trade(
            db=db,
            request=request,
        )

    except ValueError as e:
        # Domain validation errors
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        # Print full traceback to terminal for debugging
        logger.error("[STEP4][PREVIEW][UNEXPECTED ERROR]")
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

    try:
        return freeze_step4_trade(
            db=db,
            request=request,
        )

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