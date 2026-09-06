#/IntradayTradeStockAnalyser/backend/services/live_service.py
import os
from typing import List, Dict, Any

import httpx
import socket
from urllib.parse import urlparse
import time

BASE_URL = os.getenv("ZERODHA_MARKET_DATA_BASE_URL", "http://127.0.0.1:8001")


class LiveService:

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

            candles = [
                LiveService._normalize_candle(c)
                for c in candles_raw
            ]

            return {
                "status": "success",
                "trade_date": payload.get("trade_date"),
                "interval": payload.get("interval"),
                "contract": payload.get("contract"),
                "candles": candles,
                "count": payload.get("count", len(candles)),
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

            candles = [
                LiveService._normalize_candle(c)
                for c in candles_raw
            ]

            return {
                "status": "success",
                "symbol": payload.get("symbol"),
                "trade_date": payload.get("trade_date"),
                "interval": payload.get("interval"),
                "candles": candles,
                "count": payload.get("count", len(candles)),
            }

        except Exception as e:
            print("LIVE_SERVICE request failed")
            print("exception_type=", type(e))
            print("exception=", repr(e))
            return {
                "status": "error",
                "message": str(e)
            }
