# =========================================================
# File: backend/app/api/step3.py
# =========================================================
"""
STEP-3 API — Hybrid Manual Mode (Automation-Ready)

ARCHITECTURAL NOTE
------------------

Phase-1 (Hybrid Manual Mode):
    - UI provides full Step3StockContext inputs.
    - Backend evaluates deterministically.
    - Freeze persists only final evaluated candidates.

Future Automation Migration:
    - Compute endpoint will internally construct Step3StockContext
      from stock data pipeline.
    - Manual metrics will be removed from UI.
    - Evaluation engine will remain unchanged.
"""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging
import traceback

from backend.app.db.session import get_db
from backend.app.schemas.step3_schema import (
    Step3ExecutionResponse,
    Step3ComputeRequest,
    Step3ComputeResponse,
    Step3FreezeRequest,
    Step3FreezeResponse,
)
from backend.app.services.step3_service import (
    generate_step3_execution,
    compute_step3_candidates,
    freeze_step3_candidates,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/step3",
    tags=["STEP-3"],
)


# =========================================================
# PREVIEW — Read Only
# =========================================================

class Step3PreviewRequest(BaseModel):
    trade_date: date = Field(...)


@router.post(
    "/preview",
    response_model=Step3ExecutionResponse,
    status_code=status.HTTP_200_OK,
)
def preview_step3(
    request: Step3PreviewRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        "[STEP3][API][PREVIEW][START] trade_date=%s",
        request.trade_date,
    )

    try:
        response = generate_step3_execution(
            db=db,
            trade_date=request.trade_date,
        )

        logger.info(
            "[STEP3][API][PREVIEW][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return response

    except Exception as e:
        logger.error(
            "[STEP3][API][PREVIEW][ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# =========================================================
# COMPUTE — Evaluate Only (Hybrid Input)
# =========================================================

@router.post(
    "/compute",
    response_model=Step3ComputeResponse,
    status_code=status.HTTP_200_OK,
)
def compute_step3(
    request: Step3ComputeRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        "[STEP3][API][COMPUTE][START] trade_date=%s stock_count=%s",
        request.trade_date,
        len(request.stocks),
    )

    try:
        response = compute_step3_candidates(
            db=db,
            trade_date=request.trade_date,
            stocks=request.stocks,
        )

        logger.info(
            "[STEP3][API][COMPUTE][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return response

    except Exception as e:
        logger.error(
            "[STEP3][API][COMPUTE][ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# =========================================================
# FREEZE — Persist Final Evaluated Output
# =========================================================

@router.post(
    "/freeze",
    response_model=Step3FreezeResponse,
    status_code=status.HTTP_200_OK,
)
def freeze_step3(
    request: Step3FreezeRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        "[STEP3][API][FREEZE][START] trade_date=%s candidates=%s",
        request.trade_date,
        len(request.candidates),
    )

    try:
        response = freeze_step3_candidates(
            db=db,
            trade_date=request.trade_date,
            candidates=request.candidates,
        )

        logger.info(
            "[STEP3][API][FREEZE][SUCCESS] trade_date=%s",
            request.trade_date,
        )

        return response

    except Exception as e:
        logger.error(
            "[STEP3][API][FREEZE][ERROR] trade_date=%s error=%s",
            request.trade_date,
            str(e),
        )
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
