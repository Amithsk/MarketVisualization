#IntradayTradeStockAnalyser/backend/api/replay.py
from fastapi import (
    APIRouter,
    Depends,
    Body
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
from backend.services.replay_stock_fetch_service import (
    ReplayStockFetchError,
    ReplayStockFetchService,
)

router = APIRouter()


@router.post("/api/v1/replay/stock-candles/fetch")
async def fetch_replay_stock_candles(payload: dict = Body(...)):
    trade_date = payload.get("trade_date") if isinstance(payload, dict) else None
    symbol = payload.get("symbol") if isinstance(payload, dict) else None
    try:
        result = ReplayStockFetchService.fetch(trade_date, symbol)
        return JSONResponse(status_code=200, content={"status": "success", "message": "Historical stock candles fetched successfully", "data": result})
    except ReplayStockFetchError as error:
        print(f"Replay stock fetch failed: code={error.code}")
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": str(error), "data": {"trade_date": trade_date, "symbol": (symbol or "").strip().upper(), "replay_ready": False}})
    except Exception:
        print("Replay stock fetch failed: code=INTERNAL_ERROR")
        return JSONResponse(status_code=500, content={"status": "error", "error_code": "INTERNAL_ERROR", "message": "Unable to prepare historical stock candles", "data": {"trade_date": trade_date, "symbol": (symbol or "").strip().upper(), "replay_ready": False}})


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

    except ReplayStockFetchError as error:

        return JSONResponse(
            status_code=error.status_code,
            content={
                "status": "error",
                "error_code": error.code,
                "message": str(error)
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
