from fastapi import (
    APIRouter,
    Depends
)

from fastapi.responses import (
    JSONResponse
)

from sqlalchemy.orm import Session

from backend.services.replay_service import (
    ReplayService
)

from backend.utils.deps import (
    get_db
)

router = APIRouter()


@router.get("/api/v1/replay")
async def get_replay_data(
    trade_date: str,
    stock: str,
    db: Session = Depends(get_db)
):

    try:

        print(
            "\n===== FETCHING REPLAY DATA ====="
        )

        print(
            f"Trade Date: {trade_date}"
        )

        print(
            f"Stock: {stock}"
        )

        replay_data = (
            ReplayService
            .get_replay_data(
                db,
                trade_date,
                stock
            )
        )

        print(
            "Replay payload generated"
        )

        print(
            "================================\n"
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "replay_data": replay_data
            }
        )

    except Exception as error:

        print(
            "\n===== REPLAY API FAILED ====="
        )

        print(str(error))

        print(
            "================================\n"
        )

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(error)
            }
        )