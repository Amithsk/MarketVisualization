#IntradayTradeStockAnalyser/backend/api/replay.py
from fastapi import (
    APIRouter,
    Depends,
)

from fastapi.responses import (
    JSONResponse
)

from sqlalchemy.orm import Session

from backend.services.replay_service import (
    ReplayService
)
from backend.repositories.replay_repository import (
    ExecutedTradeNotFoundError,
    MultipleExecutedTradesError,
)

from backend.utils.deps import (
    get_db
)
from backend.services.replay_stock_fetch_service import (
    ReplayStockFetchError,
    ReplayStockFetchService,
)
from backend.services.replay_coach_context_service import ReplayCoachContextService, ReplayCoachContextValidationError
from backend.services.replay_coach_openai_service import ReplayCoachError
from backend.services.replay_coach_service import ReplayCoachService
from backend.models.replay_model import ReplayStockFetchRequest

router = APIRouter()


@router.post("/api/v1/replay/stock-candles/fetch")
async def fetch_replay_stock_candles(request: ReplayStockFetchRequest):
    trade_date = request.trade_date
    symbol = request.symbol
    try:
        result = ReplayStockFetchService.fetch(trade_date, symbol)
        return JSONResponse(status_code=200, content={"status": "success", "message": "Historical stock candles fetched successfully", "data": result})
    except ReplayStockFetchError as error:
        print(f"Replay stock fetch failed: code={error.code}")
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": str(error), "data": {"trade_date": trade_date.isoformat(), "symbol": symbol, "replay_ready": False}})
    except Exception:
        print("Replay stock fetch failed: code=INTERNAL_ERROR")
        return JSONResponse(status_code=500, content={"status": "error", "error_code": "INTERNAL_ERROR", "message": "Unable to prepare historical stock candles", "data": {"trade_date": trade_date.isoformat(), "symbol": symbol, "replay_ready": False}})


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

    except ExecutedTradeNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "status": "executed_trade_not_found",
                "message": (
                    "No executed TradeJournal trade found for "
                    f"{stock.strip().upper().removeprefix('NSE:')} on {trade_date}."
                ),
            },
        )

    except MultipleExecutedTradesError as error:
        return JSONResponse(
            status_code=409,
            content={
                "status": "multiple_executed_trades",
                "message": (
                    "Multiple executed TradeJournal trades found for "
                    f"{stock.strip().upper().removeprefix('NSE:')} on {trade_date}."
                ),
                "trade_ids": error.trade_ids,
            },
        )

    except Exception as error:
        print("\n===== REPLAY API FAILED =====")
        print(str(error))
        print("================================\n")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(error)})


@router.get("/api/v1/replay/coach/context")
async def get_replay_coach_context(trade_date: str, stock: str, db: Session = Depends(get_db)):
    """Developer preview of raw Coach evidence; does not invoke an LLM."""
    try:
        replay_data = ReplayService.get_replay_data(db, trade_date, stock)
        coach_context = ReplayCoachContextService.build_context(replay_data, trade_date)
        return JSONResponse(status_code=200, content={"status": "success", "coach_context": coach_context})
    except ExecutedTradeNotFoundError:
        return JSONResponse(status_code=404, content={"status": "executed_trade_not_found", "message": f"No executed trade found for {stock.strip().upper().removeprefix('NSE:')} on {trade_date}."})
    except ReplayCoachContextValidationError as error:
        return JSONResponse(status_code=422, content={"status": "coach_context_invalid", "message": "Replay data cannot be used for Coach analysis.", "errors": error.errors})
    except MultipleExecutedTradesError as error:
        return JSONResponse(status_code=409, content={"status": "multiple_executed_trades", "message": str(error), "trade_ids": error.trade_ids})
    except ReplayStockFetchError as error:
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": str(error)})
    except Exception as error:
        print(f"Replay Coach context preview failed: {error}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(error)})


@router.post("/api/v1/replay/coach/start")
async def start_replay_coach(trade_date: str, stock: str, db: Session = Depends(get_db)):
    """Create one OpenAI-backed Coach review from validated Replay evidence."""
    try:
        replay_data = ReplayService.get_replay_data(db, trade_date, stock)
        coach_context = ReplayCoachContextService.build_context(replay_data, trade_date)
        result = ReplayCoachService.start(coach_context)
        return JSONResponse(status_code=200, content={
            "status": "success", "trade_date": coach_context["trade_date"],
            "stock": coach_context["stock"]["symbol"], **result,
        })
    except ReplayCoachContextValidationError as error:
        return JSONResponse(status_code=422, content={"status": "coach_context_invalid", "message": "Replay data cannot be used for Coach analysis.", "errors": error.errors})
    except ReplayCoachError as error:
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": error.public_message})
    except ExecutedTradeNotFoundError:
        return JSONResponse(status_code=404, content={"status": "executed_trade_not_found", "message": f"No executed trade found for {stock.strip().upper().removeprefix('NSE:')} on {trade_date}."})
    except MultipleExecutedTradesError as error:
        return JSONResponse(status_code=409, content={"status": "multiple_executed_trades", "message": str(error), "trade_ids": error.trade_ids})
    except ReplayStockFetchError as error:
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": str(error)})
    except Exception:
        return JSONResponse(status_code=500, content={"status": "error", "error_code": "REPLAY_COACH_FAILED", "message": "Replay Coach analysis is unavailable."})
