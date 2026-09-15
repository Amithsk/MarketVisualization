from datetime import datetime, timezone
from types import SimpleNamespace
import unittest

from fastapi import HTTPException

from app.market_time import to_api_time, to_storage_time
from app.routers.trades import exit_trade
from app.schemas import ExitTradePayload


class FakeSession:
    def __init__(self, trade):
        self.trade = trade
        self.committed = False

    def get(self, model, trade_id):
        return self.trade

    def commit(self):
        self.committed = True


class MarketTimeTests(unittest.TestCase):
    def test_converts_utc_input_to_india_market_wall_time(self):
        utc_time = datetime(2026, 9, 11, 5, 59, tzinfo=timezone.utc)

        stored = to_storage_time(utc_time)

        self.assertEqual(stored, datetime(2026, 9, 11, 11, 29))
        self.assertEqual(
            to_api_time(stored),
            "2026-09-11T11:29:00+05:30",
        )

    def test_preserves_naive_market_wall_time_and_adds_offset_on_response(self):
        stored = to_storage_time(datetime(2026, 9, 11, 10, 53))

        self.assertEqual(stored, datetime(2026, 9, 11, 10, 53))
        self.assertEqual(
            to_api_time(stored),
            "2026-09-11T10:53:00+05:30",
        )

    def test_rejects_exit_before_entry(self):
        session = FakeSession(SimpleNamespace(
            exit_timestamp=None,
            timestamp=datetime(2026, 9, 11, 10, 53),
        ))
        payload = ExitTradePayload(
            exit_price=997,
            exit_reason="TARGET_HIT",
            exit_timestamp=datetime.fromisoformat("2026-09-11T04:59:00+00:00"),
        )

        with self.assertRaises(HTTPException) as error:
            exit_trade(145, payload, session)

        self.assertEqual(error.exception.status_code, 422)
        self.assertFalse(session.committed)

    def test_stores_exit_in_market_time_and_returns_offset(self):
        trade = SimpleNamespace(
            exit_timestamp=None,
            timestamp=datetime(2026, 9, 11, 10, 53),
        )
        session = FakeSession(trade)
        payload = ExitTradePayload(
            exit_price=997,
            exit_reason="TARGET_HIT",
            exit_timestamp=datetime.fromisoformat("2026-09-11T05:59:00+00:00"),
        )

        result = exit_trade(145, payload, session)

        self.assertTrue(session.committed)
        self.assertEqual(trade.exit_timestamp, datetime(2026, 9, 11, 11, 29))
        self.assertEqual(result["exit_timestamp"], "2026-09-11T11:29:00+05:30")
