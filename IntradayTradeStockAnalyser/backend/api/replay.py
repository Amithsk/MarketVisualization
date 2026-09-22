#IntradayTradeStockAnalyser/backend/api/replay.py
import hashlib
import json
import logging
from time import perf_counter
from uuid import uuid4
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
from backend.services.replay_coach_service import ReplayCoachService, ReplayCoachLifecycle
from backend.models.replay_model import ReplayStockFetchRequest

router = APIRouter()
logger = logging.getLogger(__name__)


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
    request_id, started = uuid4().hex[:12], perf_counter()
    lifecycle = ReplayCoachLifecycle(request_id=request_id, started_at=started)
    symbol = stock.strip().upper().removeprefix("NSE:")
    logger.info("Replay Coach request started: request_id=%s method=POST path=/api/v1/replay/coach/start trade_date=%s symbol=%s", request_id, trade_date, symbol)
    try:
        replay_data = ReplayService.get_replay_data(db, trade_date, stock)
        coach_context = ReplayCoachContextService.build_context(replay_data, trade_date)
        canonical = json.dumps(coach_context, sort_keys=True, separators=(",", ":"), default=str)
        logger.info("Replay Coach context ready: request_id=%s trade_id=%s stock_candles=%s market_candles=%s context_version=%s evidence_hash_prefix=%s evidence_bytes=%s warnings_count=%s", request_id, coach_context["executed_trade"]["trade_id"], len(coach_context["stock"]["candles"]), len(coach_context["market"]["candles"]), coach_context.get("context_version"), hashlib.sha256(canonical.encode()).hexdigest()[:12], len(canonical.encode()), len(coach_context.get("data_quality", {})))
        result = ReplayCoachService.start(coach_context, db, request_id=request_id, lifecycle=lifecycle)
        logger.info("Replay Coach request completed: request_id=%s analysis_id=%s http_status=200 public_error_code=none result_source=%s reused=%s provider_called=%s duration_ms=%s", request_id, result.get("analysis_id"), result.get("result_source", "generated"), result.get("reused", False), result.get("result_source") != "stored", round((perf_counter()-started)*1000))
        return JSONResponse(status_code=200, content={
            "status": "success", "trade_date": coach_context["trade_date"],
            "stock": coach_context["stock"]["symbol"], **result,
        })
    except ReplayCoachContextValidationError as error:
        return JSONResponse(status_code=422, content={"status": "coach_context_invalid", "message": "Replay data cannot be used for Coach analysis.", "errors": error.errors})
    except ReplayCoachError as error:
        logger.warning("Replay Coach request completed: request_id=%s analysis_id=%s http_status=%s public_error_code=%s result_source=none reused=False provider_called=%s provider_response_received=%s provider_response_id_present=%s duration_ms=%s", request_id, lifecycle.analysis_id if lifecycle.analysis_id is not None else "none", error.status_code, error.code, lifecycle.provider_call_attempted, lifecycle.provider_response_received, bool(lifecycle.provider_response_id), round((perf_counter()-started)*1000))
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": error.public_message})
    except ExecutedTradeNotFoundError:
        return JSONResponse(status_code=404, content={"status": "executed_trade_not_found", "message": f"No executed trade found for {stock.strip().upper().removeprefix('NSE:')} on {trade_date}."})
    except MultipleExecutedTradesError as error:
        return JSONResponse(status_code=409, content={"status": "multiple_executed_trades", "message": str(error), "trade_ids": error.trade_ids})
    except ReplayStockFetchError as error:
        return JSONResponse(status_code=error.status_code, content={"status": "error", "error_code": error.code, "message": str(error)})
    except Exception as error:
        logger.error("Replay Coach request completed: request_id=%s analysis_id=%s http_status=500 public_error_code=REPLAY_COACH_FAILED result_source=none reused=False provider_called=%s provider_response_received=%s provider_response_id_present=%s duration_ms=%s exception_class=%s", request_id, lifecycle.analysis_id if lifecycle.analysis_id is not None else "none", lifecycle.provider_call_attempted, lifecycle.provider_response_received, bool(lifecycle.provider_response_id), round((perf_counter()-started)*1000), type(error).__name__)
        return JSONResponse(status_code=500, content={"status": "error", "error_code": "REPLAY_COACH_FAILED", "message": "Replay Coach analysis is unavailable."})
