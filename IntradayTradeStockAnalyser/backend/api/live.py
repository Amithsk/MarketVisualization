#/IntradayTradeStockAnalyser/backend/api/live.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.services.live_service import LiveService
from backend.services.live_nifty_poller import LiveNiftyPoller

router = APIRouter()


@router.get("/api/v1/live/nifty-candles")
async def api_nifty_candles():

    result = await LiveNiftyPoller.get_payload()

    if result.get("status") == "success":
        return JSONResponse(status_code=200, content=result)

    return JSONResponse(status_code=503, content={
        "status": "error",
        "message": result.get(
            "message",
            "Live NIFTY data temporarily unavailable"
        ),
        "trade_date": result.get("trade_date"),
        "last_error": result.get("last_error"),
    })


@router.get("/api/v1/live/symbol-candles")
async def api_symbol_candles(symbol: str):

    if not symbol:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "symbol query parameter required"
        })

    result = LiveService.get_symbol_candles(symbol)

    if result.get("status") == "success":
        return JSONResponse(status_code=200, content=result)

    return JSONResponse(status_code=502, content={
        "status": "error",
        "message": result.get("message", "Failed to fetch symbol candles")
    })
