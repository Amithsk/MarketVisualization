# backend/app/api/step2.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import traceback

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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step2",
    tags=["STEP-2"],
)


@router.post(
    "/preview",
    response_model=Step2PreviewResponse,
    status_code=status.HTTP_200_OK,
)
def preview_step2(
    request: Step2PreviewRequest,
    db: Session = Depends(get_db),
):
    """
    Preview STEP-2 Market Open Behavior.

    CONTRACT:
    - NEVER throws "data not found"
    - Returns mode = AUTO | MANUAL
    - UI decides editable vs readonly
    """

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
            "[STEP2][API][PREVIEW][SUCCESS] trade_date=%s result=%s",
            request.trade_date,
            result,
        )

        return result

    except ValueError as e:
        # Domain violation (ex: STEP-1 not frozen)

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
        # Infra / coding failure

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


@router.post(
    "/freeze",
    response_model=Step2FrozenResponse,
    status_code=status.HTTP_200_OK,
)
def freeze_step2(
    request: Step2FreezeRequest,
    db: Session = Depends(get_db),
):
    """
    Freeze STEP-2 Market Open Behavior.

    CONTRACT:
    - Accepts ONLY raw/manual inputs
    - trade_allowed is DERIVED by backend
    - reason is REQUIRED
    """

    logger.info(
        "[STEP2][API][FREEZE][START] trade_date=%s payload=%s",
        request.trade_date,
        request.dict(),
    )

    try:
        result = freeze_step2_behavior(
            db=db,
            trade_date=request.trade_date,

            # Raw observations
            index_open_behavior=request.index_open_behavior,
            early_volatility=request.early_volatility,
            market_participation=request.market_participation,

            # Mandatory manual reasoning
            reason=request.reason,
        )

        logger.info(
            "[STEP2][API][FREEZE][SUCCESS] trade_date=%s result=%s",
            request.trade_date,
            result,
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
