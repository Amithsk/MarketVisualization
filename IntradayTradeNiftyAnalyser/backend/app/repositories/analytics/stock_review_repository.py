from sqlalchemy import text
from sqlalchemy.orm import Session


class StockReviewRepository:
    """Read-only access to saved stock-review reports."""

    def __init__(self, db: Session):
        self.db = db

    def get_stocks(self, exchange: str):
        return self.db.execute(text("""
            SELECT DISTINCT exchange, symbol
            FROM intradaytrading.stock_review_daily
            WHERE exchange = :exchange
            ORDER BY symbol
        """), {"exchange": exchange}).mappings().all()

    def get_dates(self, exchange: str, symbol: str):
        return self.db.execute(text("""
            SELECT trade_date
            FROM intradaytrading.stock_review_daily
            WHERE exchange = :exchange AND symbol = :symbol
            ORDER BY trade_date DESC
        """), {"exchange": exchange, "symbol": symbol}).scalars().all()

    def get_report(self, exchange: str, symbol: str, trade_date: str):
        return self.db.execute(text("""
            SELECT exchange, symbol, trade_date, analysis_version, status,
                   session_open, session_high, session_low, session_close,
                   stock_move_points, stock_move_percent,
                   support_json, resistance_json, volume_context_json,
                   benchmark_status, benchmark_identity, benchmark_contract,
                   benchmark_expiry, comparison_json, next_session_watch_json,
                   stock_coverage_json, benchmark_coverage_json
            FROM intradaytrading.stock_review_daily
            WHERE exchange = :exchange AND symbol = :symbol AND trade_date = :trade_date
        """), {
            "exchange": exchange,
            "symbol": symbol,
            "trade_date": trade_date,
        }).mappings().first()
