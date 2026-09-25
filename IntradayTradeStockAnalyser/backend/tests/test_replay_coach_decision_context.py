import unittest
from backend.services.replay_coach_decision_context import MINIMUM_REWARD_RISK_RATIO, ReplayCoachDecisionContext


def candles(values):
    return [{"time": f"2026-09-22T{time}:00+05:30", "open": close-1, "high": close+1, "low": close-2, "close": close, "volume": volume, "vwap": close-0.5} for time, close, volume in values]


class ReplayCoachDecisionContextTests(unittest.TestCase):
    def test_entry_inside_candle_excludes_containing_and_later_candles(self):
        stock = candles([("09:55", 100, 10), ("10:00", 101, 20), ("10:05", 105, 999)])
        result = ReplayCoachDecisionContext.build(stock, stock, "2026-09-22T10:08:00+05:30", {})
        self.assertEqual(result["decision_timing"]["last_completed_stock_candle_time"], "2026-09-22T10:00:00+05:30")
        self.assertEqual(result["stock_direction"]["last_completed_close"], 101.0)

    def test_long_economics_enforces_four_to_one(self):
        result = ReplayCoachDecisionContext._economics({"entry_price": 1832.6, "stop_price": 1825, "target_price": 1835, "position_type": "LONG"})
        self.assertEqual(MINIMUM_REWARD_RISK_RATIO, 4.0)
        self.assertEqual(result["risk"], 7.6); self.assertEqual(result["reward"], 2.4)
        self.assertEqual(result["reward_risk_ratio"], 0.3158); self.assertFalse(result["take_valid"])
        self.assertEqual(result["maximum_allowed_risk"], 0.6)
        self.assertEqual(result["allowable_stop"], 1832.0)
        self.assertEqual(result["break_even_win_rate"], 0.76)
        self.assertEqual(result["equal_wins_to_recover_one_loss"], 3.1667)

    def test_short_allowable_stop_and_stock_volume_baseline(self):
        econ = ReplayCoachDecisionContext._economics({"entry_price": 100, "stop_price": 101, "target_price": 96, "position_type": "SHORT"})
        self.assertTrue(econ["take_valid"]); self.assertEqual(econ["allowable_stop"], 101.0)
        values = candles([(f"09:{15+i*5:02d}", 100+i, 100) for i in range(11)])
        values[-1]["volume"] = 150
        volume = ReplayCoachDecisionContext._volume(values)
        self.assertEqual(volume["previous_10_candle_median"], 100.0)
        self.assertEqual(volume["ratio_vs_10_candle_median"], 1.5)

    def test_isolated_extremum_is_not_a_level(self):
        values = candles([("09:15", 100, 10), ("09:20", 105, 10), ("09:25", 110, 10)])
        values[0]["low"] = 80
        self.assertEqual(ReplayCoachDecisionContext._levels(values, 100), [])
