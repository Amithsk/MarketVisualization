#/IntradayTradeStockAnalyser/backend/services/live_service.py
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from zoneinfo import ZoneInfo

import httpx
import socket
from urllib.parse import urlparse
import time
from backend.services.market_context_engine import calculate_market_context

BASE_URL = os.getenv("ZERODHA_MARKET_DATA_BASE_URL", "http://127.0.0.1:8001")
INDIAN_TIME_ZONE = ZoneInfo("Asia/Kolkata")
CANDLE_INTERVAL = timedelta(minutes=5)


class LiveService:

    @staticmethod
    def _now_ist() -> datetime:
        return datetime.now(tz=INDIAN_TIME_ZONE)

    @staticmethod
    def _candle_start_ist(value: Any) -> datetime | None:
        if value is None:
            return None

        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=INDIAN_TIME_ZONE)

        return parsed.astimezone(INDIAN_TIME_ZONE)

    @classmethod
    def _completed_candles(
        cls,
        candles: List[Dict[str, Any]],
        now_ist: datetime | None = None,
    ) -> List[Dict[str, Any]]:
        """Return only candles whose full five-minute interval has elapsed."""
        current = now_ist or cls._now_ist()
        if current.tzinfo is None:
            current = current.replace(tzinfo=INDIAN_TIME_ZONE)
        current = current.astimezone(INDIAN_TIME_ZONE)

        return [
            candle
            for candle in candles
            if (start := cls._candle_start_ist(candle.get("time"))) is not None
            and start + CANDLE_INTERVAL <= current
        ]

    @staticmethod
    def _latest_candle_timestamp(candles: List[Dict[str, Any]]) -> Any:
        return candles[-1].get("time") if candles else None

    @staticmethod
    def _normalize_candle(raw: Dict[str, Any]) -> Dict[str, Any]:
        # Map nsetradebot fields to application candle model
        # Expecting keys like Datetime, Open, High, Low, Close, Volume
        return {
            "time": raw.get("Datetime") or raw.get("time") or raw.get("datetime"),
            "open": float(raw.get("Open", raw.get("open", 0))) if raw.get("Open", raw.get("open")) is not None else None,
            "high": float(raw.get("High", raw.get("high", 0))) if raw.get("High", raw.get("high")) is not None else None,
            "low": float(raw.get("Low", raw.get("low", 0))) if raw.get("Low", raw.get("low")) is not None else None,
            "close": float(raw.get("Close", raw.get("close", 0))) if raw.get("Close", raw.get("close")) is not None else None,
            "volume": int(raw.get("Volume", raw.get("volume", 0))) if raw.get("Volume", raw.get("volume")) is not None else 0,
        }

    @staticmethod
    def get_nifty_candles() -> Dict[str, Any]:
        url = f"{BASE_URL}/zerodha/nifty-futures/candles"

        try:
            print("LIVE_SERVICE request")
            print(f"base_url={BASE_URL}")
            print(f"url={url}")
            print("method=GET")
            print("timeout=10.0")
            print("proxy env:", {
                "HTTP_PROXY": os.getenv("HTTP_PROXY"),
                "http_proxy": os.getenv("http_proxy"),
                "HTTPS_PROXY": os.getenv("HTTPS_PROXY"),
                "https_proxy": os.getenv("https_proxy"),
                "NO_PROXY": os.getenv("NO_PROXY"),
                "no_proxy": os.getenv("no_proxy"),
            })

            # TCP connectivity diagnostic
            try:
                parsed = urlparse(BASE_URL)
                host = parsed.hostname
                port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                start = time.time()
                print(f"Attempting TCP connect to {host}:{port}")
                sock = socket.create_connection((host, port), timeout=5)
                elapsed = time.time() - start
                print(f"TCP connect succeeded in {elapsed:.3f}s")
                sock.close()
            except Exception as sock_e:
                print("TCP connect failed:", repr(sock_e))

            r = httpx.get(url,    headers={        "User-Agent": "curl/7.88.1",        "Connection": "close",        "Accept": "*/*",    },    timeout=15.0,)
            r.raise_for_status()
            payload = r.json()

            # Normalize candles
            candles_raw = payload.get("candles", [])

            normalized_candles = [
                LiveService._normalize_candle(c)
                for c in candles_raw
            ]
            now_ist = LiveService._now_ist()
            candles = LiveService._completed_candles(
                normalized_candles,
                now_ist,
            )
            upstream_latest = LiveService._latest_candle_timestamp(
                normalized_candles,
            )
            latest_completed = LiveService._latest_candle_timestamp(candles)

            return {
                "status": "success",
                "trade_date": payload.get("trade_date"),
                "interval": payload.get("interval"),
                "contract": payload.get("contract"),
                "candles": candles,
                "count": len(candles),
                "upstream_latest_candle_timestamp": upstream_latest,
                "latest_completed_candle_timestamp": latest_completed,
                "market_context": calculate_market_context(candles, "NIFTY-FUT"),
            }

        except Exception as e:
            print("LIVE_SERVICE request failed")
            print("exception_type=", type(e))
            print("exception=", repr(e))
            return {
                "status": "error",
                "message": str(e)
            }

    @staticmethod
    def get_symbol_candles(symbol: str) -> Dict[str, Any]:
        url = f"{BASE_URL}/zerodha/symbol/candles"
        params = {"symbol": symbol}

        try:
            full_url = f"{url}?symbol={symbol}"
            print("LIVE_SERVICE request")
            print(f"base_url={BASE_URL}")
            print(f"url={full_url}")
            print("method=GET")
            print("timeout=10.0")
            print("proxy env:", {
                "HTTP_PROXY": os.getenv("HTTP_PROXY"),
                "http_proxy": os.getenv("http_proxy"),
                "HTTPS_PROXY": os.getenv("HTTPS_PROXY"),
                "https_proxy": os.getenv("https_proxy"),
                "NO_PROXY": os.getenv("NO_PROXY"),
                "no_proxy": os.getenv("no_proxy"),
            })

            # TCP connectivity diagnostic
            try:
                parsed = urlparse(BASE_URL)
                host = parsed.hostname
                port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                start = time.time()
                print(f"Attempting TCP connect to {host}:{port}")
                sock = socket.create_connection((host, port), timeout=5)
                elapsed = time.time() - start
                print(f"TCP connect succeeded in {elapsed:.3f}s")
                sock.close()
            except Exception as sock_e:
                print("TCP connect failed:", repr(sock_e))

            with httpx.Client(timeout=10.0) as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                payload = r.json()

            candles_raw = payload.get("candles", [])

            normalized_candles = [
                LiveService._normalize_candle(c)
                for c in candles_raw
            ]
            now_ist = LiveService._now_ist()
            candles = LiveService._completed_candles(
                normalized_candles,
                now_ist,
            )
            upstream_latest = LiveService._latest_candle_timestamp(
                normalized_candles,
            )
            latest_completed = LiveService._latest_candle_timestamp(candles)

            print(
                "[STOCK_LIVE] "
                f"instrument={payload.get('symbol') or symbol} "
                f"now_ist={now_ist.isoformat()} "
                f"upstream_latest={upstream_latest} "
                f"latest_completed={latest_completed} "
                f"returned_latest={latest_completed}"
            )

            return {
                "status": "success",
                "symbol": payload.get("symbol"),
                "trade_date": payload.get("trade_date"),
                "interval": payload.get("interval"),
                "candles": candles,
                "count": len(candles),
                "upstream_latest_candle_timestamp": upstream_latest,
                "latest_completed_candle_timestamp": latest_completed,
                "market_context": calculate_market_context(candles, payload.get("symbol") or symbol),
            }

        except Exception as e:
            print("LIVE_SERVICE request failed")
            print("exception_type=", type(e))
            print("exception=", repr(e))
            return {
                "status": "error",
                "message": str(e)
            }
