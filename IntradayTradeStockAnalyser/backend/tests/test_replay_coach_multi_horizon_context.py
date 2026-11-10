import unittest

from backend.services.replay_coach_decision_context import ReplayCoachDecisionContext as Context


def candles(points):
    return [{"time": f"2026-10-29T09:{15 + index * 5:02d}:00+05:30", "open": close, "high": high, "low": low, "close": close, "volume": volume, "vwap": vwap} for index, (high, low, close, volume, vwap) in enumerate(points)]


class MultiHorizonDecisionContextTests(unittest.TestCase):
    def test_confirmed_swings_classify_bullish_and_bearish_without_future_candles(self):
        bullish = candles([(101, 99, 100, 100, 100), (103, 100, 102, 100, 100), (102, 98, 101, 100, 100), (105, 102, 104, 100, 100), (104, 101, 103, 100, 100), (107, 104, 106, 100, 100), (106, 103, 105, 100, 100)])
        bearish = candles([(107, 105, 106, 100, 106), (106, 103, 104, 100, 106), (108, 104, 105, 100, 106), (104, 101, 102, 100, 106), (105, 102, 103, 100, 106), (102, 99, 100, 100, 106), (103, 100, 101, 100, 106)])
        self.assertEqual(Context._structure(bullish)["classification"], "BULLISH")
        self.assertEqual(Context._structure(bearish)["classification"], "BEARISH")
        self.assertEqual(Context._structure(bullish[:-3])["classification"], "INSUFFICIENT_DATA")

    def test_momentum_vwap_and_composite_remain_separate(self):
        values = candles([(101, 99, 100, 100, 100), (103, 100, 102, 100, 100), (102, 98, 101, 100, 100), (105, 102, 104, 100, 100), (104, 101, 103, 100, 100), (107, 104, 106, 100, 100), (106, 103, 105, 100, 100)])
        structure = Context._structure(values)
        self.assertEqual(structure["classification"], "BULLISH")
        self.assertEqual(Context._momentum(values)["classification"], "BULLISH")
        near = Context._vwap([{"high": 1376, "low": 1374, "close": 1375.3, "vwap": 1376.41}])
        self.assertEqual(near["location"], "NEAR")
        self.assertEqual(Context._composite("BULLISH", "BEARISH"), "BULLISH_STRUCTURE_PULLBACK")
        self.assertEqual(Context._composite("BEARISH", "BULLISH"), "BEARISH_STRUCTURE_BOUNCE")

    def test_vwap_boundaries_and_decision_cutoff(self):
        near = Context._vwap([{"high": 102, "low": 98, "close": 100.4, "vwap": 100}])
        self.assertEqual(near["location"], "NEAR")  # 0.4 is the 15% range tolerance
        self.assertEqual(Context._vwap([{"high": 102, "low": 98, "close": 100.6001, "vwap": 100}])["location"], "ABOVE")
        self.assertEqual(Context._vwap([{"high": 102, "low": 98, "close": 99.3999, "vwap": 100}])["location"], "BELOW")
        self.assertEqual(Context._vwap([{"high": 102, "low": 98, "close": 100, "vwap": None}])["location"], "UNAVAILABLE")
        values = candles([(101, 99, 100, 100, 100), (103, 100, 102, 100, 100), (102, 98, 101, 100, 100), (105, 102, 104, 100, 100), (104, 101, 103, 100, 100), (107, 104, 106, 100, 100), (106, 103, 105, 9999, 100)])
        completed = Context._completed(values, __import__("datetime").datetime.fromisoformat("2026-10-29T09:45:00+05:30"))
        self.assertEqual(len(completed), 6)
        self.assertNotEqual(completed[-1]["volume"], 9999)

    def test_volume_and_relationship_categories(self):
        self.assertEqual(Context._volume_context({"ratio_vs_5_candle_median": 1.2})["classification"], "STRONG")
        self.assertEqual(Context._volume_context({"ratio_vs_5_candle_median": .8})["classification"], "NORMAL")
        self.assertEqual(Context._volume_context({"ratio_vs_5_candle_median": .7})["classification"], "WEAK")
        self.assertEqual(Context._volume_context({})["classification"], "UNAVAILABLE")
        self.assertEqual(Context._relationship("BULLISH", "BULLISH", "BULLISH", "BULLISH")["classification"], "NIFTY_BULLISH_STOCK_BULLISH")
        self.assertEqual(Context._relationship("MIXED", "BEARISH", "BULLISH", "BULLISH")["classification"], "NIFTY_BULLISH_STOCK_WEAK")
        self.assertEqual(Context._relationship("BULLISH", "BULLISH", "BEARISH", "BEARISH")["classification"], "NIFTY_WEAK_STOCK_BULLISH")
        self.assertEqual(Context._relationship("BEARISH", "BEARISH", "BEARISH", "BEARISH")["classification"], "NIFTY_WEAK_STOCK_WEAK")
        self.assertEqual(Context._relationship("INSUFFICIENT_DATA", "NEUTRAL", "INSUFFICIENT_DATA", "NEUTRAL")["classification"], "MIXED_OR_UNCLEAR")
