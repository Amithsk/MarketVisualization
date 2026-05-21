from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.services.trade_service import (
    TradeService
)

from  backend.utils.deps import get_db


router = APIRouter()


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