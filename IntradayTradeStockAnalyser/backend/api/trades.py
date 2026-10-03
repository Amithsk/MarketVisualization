from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.services.trade_service import (
    TradeService
)

from  backend.utils.deps import get_db
from backend.services.trade_plan_draft_service import TradePlanDraftError, TradePlanDraftService


router = APIRouter()


class DraftCandle(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class TradePlanDraftRequest(BaseModel):
    direction: str
    strategy: str
    context_timestamp: str
    stock_candles: list[DraftCandle] = Field(default_factory=list)
    nifty_candles: list[DraftCandle] = Field(default_factory=list)
    entry: str | None = None
    stop_loss: str | None = None
    target: str | None = None
    invalidation: str | None = None
    entry_confirmation: str | None = None


@router.post("/api/v1/trades/plan-draft")
async def create_trade_plan_draft(request: TradePlanDraftRequest):
    """Build an editable, deterministic description from supplied completed evidence."""
    try:
        return {"status": "success", **TradePlanDraftService.build(request.model_dump())}
    except TradePlanDraftError as error:
        raise HTTPException(status_code=422, detail=str(error))


@router.get("/api/v1/trades/dates")
async def get_trade_dates(
    db: Session = Depends(get_db)
):

    try:

        print(
            "\n===== FETCHING TRADE DATES ====="
        )

        dates = (
            TradeService
            .get_trade_dates(db)
        )

        print(
            f"Total trade dates: {len(dates)}"
        )

        print("================================\n")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "trade_dates": dates
            }
        )

    except Exception as error:

        print(
            "\n===== TRADE DATES API FAILED ====="
        )

        print(str(error))

        print("==================================\n")

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(error)
            }
        )
    
@router.get("/api/v1/trades/stocks")
async def get_traded_stocks(
    trade_date: str,
    db: Session = Depends(get_db)
):

    try:

        print(
            "\n===== FETCHING TRADED STOCKS ====="
        )

        print(
            f"Trade Date: {trade_date}"
        )

        stocks = (
            TradeService
            .get_traded_stocks(
                db,
                trade_date
            )
        )

        print(
            f"Total Stocks: {len(stocks)}"
        )

        print("==================================\n")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "stocks": stocks
            }
        )

    except Exception as error:

        print(
            "\n===== TRADED STOCK API FAILED ====="
        )

        print(str(error))

        print("===================================\n")

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(error)
            }
        )
