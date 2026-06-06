from fastapi import (
    APIRouter,
    Depends
)

from fastapi.responses import (
    JSONResponse
)

from sqlalchemy.orm import Session

from backend.services.nifty_service import (
    NiftyService
)

from backend.utils.deps import (
    get_db
)

router = APIRouter()


@router.get("/api/v1/nifty/candles")
async def get_nifty_candles(
    trade_date: str,
    db: Session = Depends(get_db)
):

    try:

        print(
            "\n===== FETCHING NIFTY CANDLES ====="
        )

        print(
            f"Trade Date: {trade_date}"
        )

        candles = (
            NiftyService
            .get_nifty_candles(
                db,
                trade_date
            )
        )

        print(
            f"Total Candles: {len(candles)}"
        )

        print("==================================\n")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "candles": candles
            }
        )

    except Exception as error:

        print(
            "\n===== NIFTY API FAILED ====="
        )

        print(str(error))

        print("================================\n")

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(error)
            }
        )