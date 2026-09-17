from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from backend.repositories.nifty_repository import NiftyRepository


class FakeResult:
    def fetchall(self):
        return [(datetime(2026, 9, 16, 9, 15), 100, 102, 99, 101, Decimal("196170"))]


class FakeSession:
    def __init__(self):
        self.statement = None

    def execute(self, statement, parameters):
        self.statement = str(statement)
        self.parameters = parameters
        return FakeResult()


class NiftyRepositoryTests(TestCase):
    def test_maps_database_volume_with_explicit_lowercase_alias(self):
        db = FakeSession()

        candle = NiftyRepository.get_nifty_candles(db, "2026-09-16")[0]

        self.assertIn("P.Volume AS volume", db.statement)
        self.assertEqual(candle.time, datetime(2026, 9, 16, 9, 15))
        self.assertEqual(candle.volume, Decimal("196170"))
        self.assertIsNone(candle.vwap)
