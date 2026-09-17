from datetime import datetime
from decimal import Decimal
import unittest

from backend.repositories.replay_repository import (
    ExecutedTradeNotFoundError,
    MultipleExecutedTradesError,
    ReplayRepository,
)


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.params = None

    def execute(self, query, params):
        self.params = params
        return FakeResult(self.rows)


def execution_row(**overrides):
    row = {
        "trade_plan_id": 123,
        "trade_id": 456,
        "entry_timestamp": datetime(2026, 9, 11, 10, 50),
        "symbol": "SBIN",
        "order_id": None,
        "side": "SELL",
        "quantity": 100,
        "price": Decimal("994.60"),
        "status": "filled",
        "entry_price": Decimal("994.60"),
        "exit_price": Decimal("997.00"),
        "exit_timestamp": datetime(2026, 9, 11, 11, 10),
        "pnl_amount": Decimal("-240.00"),
        "pnl_pct": Decimal("-0.24"),
        "trade_result": "loss",
        "exit_reason": None,
    }
    row.update(overrides)
    return row


class ReplayExecutedTradeRepositoryTests(unittest.TestCase):
    def test_returns_single_execution_and_serializes_nullable_decimals(self):
        session = FakeSession([execution_row(exit_price=None, pnl_amount=None)])

        result = ReplayRepository.get_executed_trade(
            session, "2026-09-11", "NSE:sbin"
        )

        self.assertEqual(session.params["stock"], "SBIN")
        self.assertEqual(result["trade_plan_id"], 123)
        self.assertEqual(result["trade_id"], 456)
        self.assertEqual(result["entry_price"], 994.60)
        self.assertEqual(result["entry_timestamp"], "2026-09-11T10:50:00")
        self.assertIsNone(result["exit_price"])
        self.assertIsNone(result["pnl_amount"])
        self.assertEqual(result["execution_source"], "TRADE_JOURNAL")

    def test_raises_not_found_when_no_executed_trade_matches(self):
        with self.assertRaises(ExecutedTradeNotFoundError):
            ReplayRepository.get_executed_trade(
                FakeSession([]), "2026-09-11", "SBIN"
            )

    def test_raises_for_multiple_executed_trades(self):
        session = FakeSession([
            execution_row(trade_id=456),
            execution_row(trade_id=789),
        ])

        with self.assertRaises(MultipleExecutedTradesError) as error:
            ReplayRepository.get_executed_trade(
                session, "2026-09-11", "SBIN"
            )

        self.assertEqual(error.exception.trade_ids, [456, 789])
