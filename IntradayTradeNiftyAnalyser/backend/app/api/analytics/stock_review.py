from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.analytics.stock_review import StockIdentitySchema, StockReviewResponseSchema
from backend.app.services.analytics.stock_review_service import StockReviewService

router = APIRouter(prefix="/api/analytics/stock-reviews", tags=["Analytics"])


@router.get("/stocks", response_model=list[StockIdentitySchema])
def get_stocks(exchange: str = Query("NSE"), db: Session = Depends(get_db)):
    return StockReviewService(db).get_stocks(exchange)


@router.get("/{exchange}/{symbol}/dates")
def get_dates(exchange: str, symbol: str, db: Session = Depends(get_db)):
    return StockReviewService(db).get_dates(exchange, symbol)


@router.get("/{exchange}/{symbol}/{trade_date}", response_model=StockReviewResponseSchema)
def get_report(exchange: str, symbol: str, trade_date: date, db: Session = Depends(get_db)):
    report = StockReviewService(db).get_report(exchange, symbol, trade_date.isoformat())
    if report is None:
        raise HTTPException(status_code=404, detail="Saved stock review not found")
    return report
