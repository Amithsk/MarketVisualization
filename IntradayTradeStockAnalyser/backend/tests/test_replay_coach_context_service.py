import copy
import unittest
from decimal import Decimal

from backend.services.replay_coach_context_service import (
    ReplayCoachContextService,
    ReplayCoachContextValidationError,
)


def candle(time, **values):
    return {"time": f"2026-09-11 {time}:00", "open": 100, "high": 102, "low": 99, "close": 101,
            "volume": 10, "vwap": 100.5, **values}


def replay(stock=None, market=None, **trade_values):
    trade = {"trade_plan_id": 1, "trade_id": 2, "symbol": "SBIN", "side": "BUY", "entry_price": Decimal("100.5"),
             "entry_timestamp": "2026-09-11T09:18:00", "exit_timestamp": "2026-09-11T09:29:00", "quantity": 1,
             "execution_source": "TRADE_JOURNAL", **trade_values}
    return {"executed_trade": trade, "stock_candles": stock or [candle("09:15"), candle("09:20"), candle("09:25")],
            "nifty_candles": market or [candle("09:15", volume=0, vwap=0), candle("09:20", volume=0, vwap=0), candle("09:25", volume=0, vwap=0)],
            "explanation_context": {"trade_coaching": "excluded"}, "market_events": ["excluded"], "trade_data": {"excluded": True}}


class ReplayCoachContextServiceTests(unittest.TestCase):
    def test_full_session_is_retained_sorted_and_source_is_unchanged(self):
        payload = replay(stock=[candle("09:25"), candle("09:15"), candle("09:20")])
        original = copy.deepcopy(payload)
        context = ReplayCoachContextService.build_context(payload, "2026-09-11")
        self.assertEqual([item["time"][11:16] for item in context["stock"]["candles"]], ["09:15", "09:20", "09:25"])
        self.assertEqual(context["stock"]["candle_count"], 3)
        self.assertEqual(payload, original)
        self.assertNotIn("market_events", context)
        self.assertNotIn("trade_data", context)
        self.assertEqual(context["executed_trade"]["entry_candle_time"], "2026-09-11T09:15:00+05:30")
        self.assertEqual(context["executed_trade"]["exit_candle_time"], "2026-09-11T09:25:00+05:30")

    def test_detects_gaps_and_unsynchronized_data(self):
        context = ReplayCoachContextService.build_context(replay(stock=[candle("09:15"), candle("09:25")]), "2026-09-11")
        self.assertEqual(context["data_quality"]["stock_missing_timestamps"], ["2026-09-11T09:20:00+05:30"])
        self.assertFalse(context["data_quality"]["timestamps_synchronized"])

    def test_duplicate_invalid_ohlc_and_bad_exit_are_rejected(self):
        with self.assertRaises(ReplayCoachContextValidationError) as result:
            ReplayCoachContextService.build_context(replay(stock=[candle("09:15"), candle("09:15", high=98)], exit_timestamp="2026-09-11T09:10:00"), "2026-09-11")
        self.assertIn("Exit timestamp occurs before entry timestamp.", result.exception.errors)
        self.assertTrue(any("duplicate" in error for error in result.exception.errors))
        self.assertTrue(any("OHLC" in error for error in result.exception.errors))

    def test_open_trade_and_unavailable_market_values(self):
        market = [
            candle("09:15", volume=None, vwap=None),
            candle("09:20", volume=None, vwap=None),
            candle("09:25", volume=None, vwap=None),
        ]
        context = ReplayCoachContextService.build_context(
            replay(market=market, exit_timestamp=None), "2026-09-11"
        )
        self.assertIsNone(context["executed_trade"]["exit_candle_time"])
        self.assertTrue(context["data_quality"]["exit_candle_found"])
        self.assertFalse(context["data_quality"]["market_volume_available"])
        self.assertIsNone(context["market"]["candles"][0]["volume"])
        self.assertIsNone(context["market"]["candles"][0]["vwap"])

    def test_market_volume_is_preserved_when_vwap_is_unavailable(self):
        market = [
            candle("09:15", volume=196170, vwap=None),
            candle("09:20", volume=None, vwap=None),
            candle("09:25", volume=71500, vwap=None),
        ]

        context = ReplayCoachContextService.build_context(replay(market=market), "2026-09-11")

        self.assertEqual(context["market"]["candles"][0]["volume"], 196170)
        self.assertIsNone(context["market"]["candles"][1]["volume"])
        self.assertEqual(context["market"]["candles"][2]["volume"], 71500)
        self.assertTrue(context["data_quality"]["market_volume_available"])
        self.assertFalse(context["data_quality"]["market_vwap_available"])

    def test_missing_trade_is_rejected(self):
        with self.assertRaises(ReplayCoachContextValidationError):
            ReplayCoachContextService.build_context({"stock_candles": [], "nifty_candles": []}, "2026-09-11")
