import json
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.repositories.analytics.stock_review_repository import StockReviewRepository


def _json(value):
    if value is None:
        return {}
    return json.loads(value) if isinstance(value, str) else value


def _plain(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


class StockReviewService:
    def __init__(self, db: Session):
        self.repository = StockReviewRepository(db)

    def get_stocks(self, exchange: str):
        return [dict(row) for row in self.repository.get_stocks(exchange)]

    def get_dates(self, exchange: str, symbol: str):
        return [{"trade_date": _plain(value)} for value in self.repository.get_dates(exchange, symbol)]

    def get_report(self, exchange: str, symbol: str, trade_date: str):
        row = self.repository.get_report(exchange, symbol, trade_date)
        if row is None:
            return None

        row = dict(row)
        stock_coverage = _json(row["stock_coverage_json"])
        coverage_header = stock_coverage.get("header", {})
        volume = _json(row["volume_context_json"])
        comparison = _json(row["comparison_json"])
        next_watch = _json(row["next_session_watch_json"])

        return {
            "header": {
                "exchange": row["exchange"], "symbol": row["symbol"],
                "trade_date": _plain(row["trade_date"]),
                "candle_interval_minutes": coverage_header.get("candle_interval_minutes", stock_coverage.get("interval_minutes")),
                "timezone": coverage_header.get("timezone", stock_coverage.get("timezone")),
            },
            "status": row["status"],
            "analysis_version": row["analysis_version"],
            "session": {
                "open": _plain(row["session_open"]), "high": _plain(row["session_high"]),
                "low": _plain(row["session_low"]), "close": _plain(row["session_close"]),
                "move_points": _plain(row["stock_move_points"]), "move_percent": _plain(row["stock_move_percent"]),
            },
            "movement": volume.get("movement"),
            "support": _json(row["support_json"]),
            "resistance": _json(row["resistance_json"]),
            "benchmark": {
                "state": comparison.get("state", "UNAVAILABLE"),
                "reason": comparison.get("reason"),
                "benchmark_status": row["benchmark_status"],
                "identity": row["benchmark_identity"], "contract": row["benchmark_contract"],
                "expiry": _plain(row["benchmark_expiry"]),
                "interval_start": comparison.get("interval", {}).get("start"),
                "interval_end": comparison.get("interval", {}).get("end"),
                "stock": comparison.get("stock"), "benchmark": comparison.get("benchmark"),
                "relationship": comparison.get("relationship"),
                "explanation": comparison.get("explanation"),
                "reference_timestamp": comparison.get("meaningful_moment_timestamp"),
                "coverage": _json(row["benchmark_coverage_json"]),
            },
            "volume_context": {key: value for key, value in volume.items() if key != "movement"},
            "next_session_watch": next_watch,
        }
