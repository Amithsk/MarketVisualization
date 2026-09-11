"""Fetch and prepare historical stock candles for the Replay store."""
import os
import re
import logging
from datetime import date, datetime, time
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

import httpx

from backend.models.candle_model import Candle
from backend.utils.replay_store import ReplayStore
from backend.validators.candle_validator import CandleValidator


IST = ZoneInfo("Asia/Kolkata")
SYMBOL_PATTERN = re.compile(r"^(?:NSE:)?[A-Z0-9]{1,30}$")
logger = logging.getLogger(__name__)


class ReplayStockFetchError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class ReplayStockFetchService:
    """Keeps Zerodha response mapping outside the route and Replay service."""

    @classmethod
    def log_market_data_configuration(cls) -> None:
        try:
            logger.info("Replay market-data base URL resolved to: %s", cls._url().removesuffix("/zerodha/symbol/historical-candles").removesuffix("/symbol/historical-candles"))
        except ReplayStockFetchError:
            logger.warning("Replay market-data base URL is not configured")

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        normalized = (symbol or "").strip().upper()
        if not normalized:
            raise ReplayStockFetchError("INVALID_REQUEST", "A stock symbol is required")
        if not SYMBOL_PATTERN.fullmatch(normalized):
            raise ReplayStockFetchError("INVALID_REQUEST", "Only NSE equity symbols are supported")
        return normalized if normalized.startswith("NSE:") else f"NSE:{normalized}"

    @staticmethod
    def validate_trade_date(trade_date: str) -> date:
        try:
            parsed = date.fromisoformat(trade_date)
        except (TypeError, ValueError):
            raise ReplayStockFetchError("INVALID_TRADE_DATE", "Trade date must be an ISO date")
        now = datetime.now(IST)
        if parsed > now.date():
            raise ReplayStockFetchError("FUTURE_TRADE_DATE", "Trade date cannot be in the future")
        if parsed == now.date() and now.time() < time(15, 30):
            raise ReplayStockFetchError(
                "MARKET_SESSION_NOT_COMPLETED",
                "Replay data is available after the NSE cash-market session closes",
            )
        return parsed

    @staticmethod
    def _url() -> str:
        base_url = os.getenv("ZERODHA_MARKET_DATA_BASE_URL", "").strip().rstrip("/")
        if not base_url:
            raise ReplayStockFetchError(
                "ZERODHA_UNAVAILABLE",
                "Replay market-data service is not configured",
                503,
            )
        if not base_url.startswith(("http://", "https://")):
            raise ReplayStockFetchError(
                "ZERODHA_UNAVAILABLE",
                "Replay market-data service URL is invalid",
                503,
            )
        suffix = "/symbol/historical-candles" if base_url.endswith("/zerodha") else "/zerodha/symbol/historical-candles"
        return f"{base_url}{suffix}"

    @staticmethod
    def _candle_rows(payload: Any) -> List[Any]:
        if not isinstance(payload, dict):
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "Historical response must be a JSON object", 502)
        data = payload.get("data")
        rows = payload.get("candles")
        if rows is None and isinstance(data, dict):
            rows = data.get("candles")
        if rows is None:
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "Historical response did not contain candles", 502)
        if not isinstance(rows, list):
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "Historical candles must be a collection", 502)
        return rows

    @staticmethod
    def _value(row: Any, *names: str) -> Any:
        if not isinstance(row, dict):
            return None
        for name in names:
            if name in row:
                return row[name]
        return None

    @classmethod
    def _map_candle(cls, row: Any, requested_date: date) -> Candle:
        if isinstance(row, (list, tuple)) and len(row) >= 6:
            raw_time, raw_open, raw_high, raw_low, raw_close, raw_volume = row[:6]
        elif isinstance(row, dict):
            raw_time = cls._value(row, "Datetime", "datetime", "timestamp", "time", "date")
            raw_open = cls._value(row, "Open", "open", "o")
            raw_high = cls._value(row, "High", "high", "h")
            raw_low = cls._value(row, "Low", "low", "l")
            raw_close = cls._value(row, "Close", "close", "c")
            raw_volume = cls._value(row, "Volume", "volume", "vol")
        else:
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "A candle has an unsupported structure", 502)
        if any(value is None or str(value).strip() == "" for value in (raw_time, raw_open, raw_high, raw_low, raw_close, raw_volume)):
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "A historical candle is missing required OHLCV data", 502)
        try:
            parsed_time = datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
            if parsed_time.tzinfo is not None:
                parsed_time = parsed_time.astimezone(IST).replace(tzinfo=None)
            volume = int(float(raw_volume))
            if float(raw_volume) != volume:
                raise ValueError("volume must be an integer")
            candle = Candle(
                time=parsed_time.strftime("%Y-%m-%d %H:%M:%S"), open=float(raw_open), high=float(raw_high),
                low=float(raw_low), close=float(raw_close), volume=volume,
            )
        except (TypeError, ValueError) as error:
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", f"Invalid historical candle value: {error}", 502)
        if parsed_time.date() != requested_date:
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "A candle does not belong to the selected trade date", 502)
        return candle

    @classmethod
    def fetch(cls, trade_date: str, symbol: str) -> Dict[str, Any]:
        requested_date = cls.validate_trade_date(trade_date)
        upstream_symbol = cls.normalize_symbol(symbol)
        normalized_symbol = upstream_symbol.removeprefix("NSE:")
        print(f"Replay stock fetch started: date={requested_date.isoformat()} symbol={normalized_symbol}")
        url = cls._url()
        logger.info("Replay historical request: url=%s symbol=%s trade_date=%s", url, upstream_symbol, requested_date)
        try:
            response = httpx.get(url, params={"symbol": upstream_symbol, "trade_date": requested_date.isoformat()}, timeout=15.0)
        except httpx.TimeoutException as error:
            logger.warning("Replay historical request timed out: url=%s error=%s", url, type(error).__name__)
            raise ReplayStockFetchError("ZERODHA_TIMEOUT", "The Zerodha historical request timed out", 504)
        except httpx.RequestError as error:
            logger.warning("Replay historical connection failure: url=%s error=%s detail=%s", url, type(error).__name__, str(error))
            raise ReplayStockFetchError("ZERODHA_UNAVAILABLE", "The Zerodha market-data service is unavailable", 503)
        logger.info("Replay historical response: url=%s status=%s", url, response.status_code)
        if response.status_code in (401, 403):
            raise ReplayStockFetchError("ZERODHA_AUTH_FAILED", "The Zerodha market-data service rejected authentication", 502)
        if response.status_code == 404:
            raise ReplayStockFetchError("SYMBOL_NOT_FOUND", f"No Zerodha symbol was found for {normalized_symbol}", 404)
        if response.status_code == 429:
            raise ReplayStockFetchError("ZERODHA_RATE_LIMITED", "The Zerodha market-data service rate limited this request", 429)
        if response.status_code >= 500:
            logger.warning("Replay historical upstream failure: url=%s status=%s", url, response.status_code)
            raise ReplayStockFetchError("ZERODHA_UNAVAILABLE", "The Zerodha market-data service is unavailable", 503)
        if response.status_code != 200:
            raise ReplayStockFetchError("INTERNAL_ERROR", "The Zerodha historical request failed", 502)
        try:
            rows = cls._candle_rows(response.json())
        except ValueError:
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", "The Zerodha response was not valid JSON", 502)
        if not rows:
            raise ReplayStockFetchError("NO_STOCK_DATA", f"No Zerodha candle data was available for {normalized_symbol} on {requested_date}", 404)
        candles = [cls._map_candle(row, requested_date) for row in rows]
        candles.sort(key=lambda candle: candle.time)
        try:
            CandleValidator.validate_candles(candles)
        except ValueError as error:
            raise ReplayStockFetchError("INVALID_CANDLE_DATA", str(error), 422)
        metadata = {"trade_date": requested_date.isoformat(), "symbol": normalized_symbol, "interval": "5minute", "source": "ZERODHA"}
        ReplayStore.set_stock_candles(candles, metadata=metadata)
        print(f"Zerodha historical request completed: candles={len(candles)}")
        print(f"Replay stock data ready: first={candles[0].time[-8:-3]} last={candles[-1].time[-8:-3]}")
        return {**metadata, "upstream_symbol": upstream_symbol, "candle_count": len(candles), "first_candle_time": candles[0].time, "last_candle_time": candles[-1].time, "replay_ready": True}
