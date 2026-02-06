from fastapi import APIRouter, Depends, HTTPException, status
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
    Preview STEP-2 market open behavior (read-only).

    Requires STEP-1 to be frozen.
    """
    try:
        return preview_step2_behavior(
            db=db,
            trade_date=request.trade_date,
        )
    except ValueError as e:
        # Domain error (STEP-1 not frozen, invalid state)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception:
        # Infrastructure / unexpected error
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
    Freeze STEP-2 market open behavior (irreversible).

    STEP-1 must already be frozen.
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
        # Domain conflict (STEP-1 not frozen, STEP-2 already frozen)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to freeze STEP-2 behavior",
        )
