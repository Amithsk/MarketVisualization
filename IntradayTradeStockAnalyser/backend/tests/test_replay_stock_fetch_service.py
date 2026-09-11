from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch
import os

from backend.services.replay_stock_fetch_service import ReplayStockFetchError, ReplayStockFetchService
from backend.utils.replay_store import ReplayStore


class FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def valid_rows():
    start = datetime(2026, 9, 10, 9, 15)
    return [{"timestamp": (start + timedelta(minutes=5 * index)).isoformat(), "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000 + index} for index in range(75)]


class ReplayStockFetchServiceTests(TestCase):
    def test_symbol_is_normalized_without_double_prefix(self):
        self.assertEqual(ReplayStockFetchService.normalize_symbol("HDFCBANK"), "NSE:HDFCBANK")
        self.assertEqual(ReplayStockFetchService.normalize_symbol("NSE:HDFCBANK"), "NSE:HDFCBANK")

    def test_missing_market_data_url_is_rejected_without_localhost_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ReplayStockFetchError, "not configured") as error:
                ReplayStockFetchService._url()
        self.assertEqual(error.exception.code, "ZERODHA_UNAVAILABLE")

    def test_fetch_maps_validated_candles_and_store_metadata(self):
        captured = {}

        def mocked_get(url, params, timeout):
            captured["params"] = params
            return FakeResponse({"candles": list(reversed(valid_rows()))})

        with patch.dict(os.environ, {"ZERODHA_MARKET_DATA_BASE_URL": "http://pi.local:8001"}), patch("backend.services.replay_stock_fetch_service.httpx.get", mocked_get):
            result = ReplayStockFetchService.fetch("2026-09-10", "HDFCBANK")
        self.assertEqual(captured["params"], {"symbol": "NSE:HDFCBANK", "trade_date": "2026-09-10"})
        self.assertEqual(result["candle_count"], 75)
        self.assertEqual(ReplayStore.get_stock_candles()[0].time, "2026-09-10 09:15:00")
        self.assertEqual(ReplayStore.get_stock_metadata()["symbol"], "HDFCBANK")

    def test_duplicate_invalid_and_empty_data_are_rejected(self):
        rows = valid_rows()
        rows[-1] = rows[0]
        with patch.dict(os.environ, {"ZERODHA_MARKET_DATA_BASE_URL": "http://pi.local:8001"}), patch("backend.services.replay_stock_fetch_service.httpx.get", return_value=FakeResponse({"candles": rows})):
            with self.assertRaisesRegex(ReplayStockFetchError, "Duplicate timestamp"):
                ReplayStockFetchService.fetch("2026-09-10", "HDFCBANK")
        rows = valid_rows()
        rows[0]["high"] = 98
        with patch.dict(os.environ, {"ZERODHA_MARKET_DATA_BASE_URL": "http://pi.local:8001"}), patch("backend.services.replay_stock_fetch_service.httpx.get", return_value=FakeResponse({"candles": rows})):
            with self.assertRaisesRegex(ReplayStockFetchError, "HIGH < OPEN"):
                ReplayStockFetchService.fetch("2026-09-10", "HDFCBANK")
        with patch.dict(os.environ, {"ZERODHA_MARKET_DATA_BASE_URL": "http://pi.local:8001"}), patch("backend.services.replay_stock_fetch_service.httpx.get", return_value=FakeResponse({"candles": []})):
            with self.assertRaises(ReplayStockFetchError) as error:
                ReplayStockFetchService.fetch("2026-09-10", "HDFCBANK")
        self.assertEqual(error.exception.code, "NO_STOCK_DATA")
