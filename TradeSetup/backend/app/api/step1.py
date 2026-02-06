from fastapi import APIRouter, Depends, HTTPException, status
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
    Preview STEP-1 pre-market context (read-only).

    Safe to call multiple times.
    Does NOT mutate state.
    """
    try:
        return preview_step1_context(
            db=db,
            trade_date=request.trade_date,
        )
    except ValueError as e:
        # Domain validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Infrastructure / unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate STEP-1 preview",
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
    Freeze STEP-1 context (irreversible).

    Once frozen, the context cannot be modified.
    """
    try:
        return freeze_step1_context(
            db=db,
            trade_date=request.trade_date,
            market_bias=request.market_bias,
            premarket_notes=request.premarket_notes,
        )
    except ValueError as e:
        # Domain conflict (already frozen, invalid transition)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        # Infrastructure / unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to freeze STEP-1 context",
        )
