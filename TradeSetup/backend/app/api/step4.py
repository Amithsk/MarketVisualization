from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.step4_schema import (
    Step4FreezeRequest,
    Step4FrozenTradeResponse,
)
from backend.app.services.step4_service import freeze_step4_trade

router = APIRouter(
    prefix="/api/step4",
    tags=["STEP-4"],
)


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

    Money-impacting.
    No recovery once frozen.
    """
    try:
        return freeze_step4_trade(
            db=db,
            request=request,
        )
    except ValueError as e:
        # Domain rule violations (expected)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception:
        # Infrastructure / unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to freeze STEP-4 trade",
        )
