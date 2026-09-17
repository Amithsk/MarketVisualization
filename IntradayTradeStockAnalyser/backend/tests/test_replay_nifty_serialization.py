from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest import TestCase

from backend.services.replay_service import ReplayService


class ReplayNiftySerializationTests(TestCase):
    def test_preserves_positive_nifty_volume_and_null_vwap(self):
        candle = SimpleNamespace(
            time=datetime(2026, 9, 16, 9, 15), open=100.0, high=102.0,
            low=99.0, close=101.0, volume=Decimal("196170"), vwap=None,
        )

        result = ReplayService._serialize_nifty_candles([candle])

        self.assertEqual(result[0]["time"], "2026-09-16 09:15:00")
        self.assertEqual(result[0]["volume"], Decimal("196170"))
        self.assertIsNone(result[0]["vwap"])
