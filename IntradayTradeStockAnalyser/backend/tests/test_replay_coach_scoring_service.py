import unittest

from backend.services.replay_coach_scoring_service import ReplayCoachScoringService


def context(pnl=100):
    return {"documented_plan": {"position_type": "SHORT"}, "executed_trade": {"pnl_amount": pnl}, "decision_context": {
        "decision_timing": {"last_completed_stock_candle_time": "2026-09-22T10:00:00+05:30"},
        "stock_direction": {"classification": "BEARISH", "last_completed_close": 100, "vwap": 101, "distance_from_vwap_points": -1, "distance_from_vwap_pct": -1},
        "nifty_direction": {"classification": "BEARISH"},
        "stock_relative_volume": {"last_completed_volume": 150, "previous_5_candle_median": 100, "ratio_vs_5_candle_median": 1.5},
        "support_resistance": [{"level_type": "RESISTANCE", "level": 101, "touch_count": 2, "established_before_entry": True}],
        "risk_economics": {"stop": 101, "risk": 1, "reward": 4, "reward_risk_ratio": 4},
    }}


class ReplayCoachScoringServiceTests(unittest.TestCase):
    def test_identical_evidence_is_stable_and_components_sum_to_total(self):
        first, second = ReplayCoachScoringService.score(context()), ReplayCoachScoringService.score(context())
        self.assertEqual(first, second)
        self.assertEqual(first["score_version"], "replay_coach_score_v1")
        self.assertEqual(first["overall_score"], sum(item["score"] for item in first["components"]))
        self.assertEqual(first["overall_score"], 10)

    def test_profit_or_loss_does_not_change_entry_score(self):
        self.assertEqual(ReplayCoachScoringService.score(context(100))["overall_score"], ReplayCoachScoringService.score(context(-100))["overall_score"])

    def test_missing_structural_stop_scores_zero_and_is_first_focus(self):
        values = context(); values["decision_context"]["support_resistance"] = []
        score = ReplayCoachScoringService.score(values)
        structure = next(item for item in score["components"] if item["component"] == "PRICE_STRUCTURE")
        self.assertEqual(structure["score"], 0)
        self.assertEqual(score["next_trade_focus"]["component"], "PRICE_STRUCTURE")
