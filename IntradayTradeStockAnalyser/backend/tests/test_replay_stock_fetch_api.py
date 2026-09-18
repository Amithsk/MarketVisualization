from datetime import date
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import app
from backend.services.replay_stock_fetch_service import ReplayStockFetchService


class ReplayStockFetchApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    @patch.object(ReplayStockFetchService, "fetch")
    def test_valid_request_calls_service_with_parsed_date_and_normalized_symbol(self, fetch):
        fetch.return_value = {"replay_ready": True, "symbol": "BHARTIARTL"}

        response = self.client.post("/api/v1/replay/stock-candles/fetch", json={"trade_date": "2026-09-16", "symbol": "  bhartiartl  "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        fetch.assert_called_once_with(date(2026, 9, 16), "BHARTIARTL")

    def test_malformed_bodies_return_422_before_service_call(self):
        invalid_bodies = [
            {"symbol": "BHARTIARTL"},
            {"trade_date": "16-09-2026", "symbol": "BHARTIARTL"},
            {"trade_date": "2026-09-16"},
            {"trade_date": "2026-09-16", "symbol": "   "},
        ]
        with patch.object(ReplayStockFetchService, "fetch") as fetch:
            for body in invalid_bodies:
                with self.subTest(body=body):
                    self.assertEqual(self.client.post("/api/v1/replay/stock-candles/fetch", json=body).status_code, 422)
        fetch.assert_not_called()
