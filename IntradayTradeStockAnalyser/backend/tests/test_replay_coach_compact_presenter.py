import unittest

from backend.models.replay_coach_model import ReplayCoachAnalysis
from backend.services.replay_coach_response_presenter import ReplayCoachResponsePresenter
from backend.services.replay_coach_service import ReplayCoachService


class CompactCoachPresenterTests(unittest.TestCase):
    def test_invalid_price_risk_returns_deterministic_decision_statuses(self):
        analysis = ReplayCoachAnalysis.model_validate({"executed_trade_analysis": {"summary": "x", "good": [], "bad": [], "how_to_improve": []}, "alternative_trade_plans": [], "key_learning": {"lesson": "x", "numeric_rule": "x", "example_using_this_trade": "x"}, "limitations": []})
        context = {"executed_trade": {"side": "BUY", "entry_price": 1832.6, "entry_timestamp": "2026-09-22T10:08:00+05:30", "pnl_amount": 72, "quantity": 1}, "documented_plan": {"position_type": "LONG"}, "decision_context": {"decision_timing": {"last_completed_stock_candle_time": "2026-09-22T10:00:00+05:30", "containing_candle_end": "2026-09-22T10:10:00+05:30"}, "stock_direction": {"classification": "BULLISH", "last_completed_close": 1832.6, "vwap": 1830.71}, "nifty_direction": {"classification": "NEUTRAL"}, "stock_relative_volume": {"last_completed_volume": 21701, "ratio_vs_5_candle_median": .5573}, "support_resistance": [], "risk_economics": {"entry": 1832.6, "stop": 1825, "target": 1835, "risk": 7.6, "reward": 2.4, "reward_risk_ratio": .3158, "required_ratio": 4.0, "break_even_win_rate": .76, "equal_wins_to_recover_one_loss": 3.1667, "take_valid": False}}}
        display = ReplayCoachResponsePresenter.coach_display(analysis, context)
        self.assertEqual(display["my_best_trade_plan"]["decision"], "WAIT")
        self.assertEqual(len(display["decision_options"]), 3)
        statuses = {option["decision"]: option["status"] for option in display["decision_options"]}
        self.assertEqual(statuses, {"TAKE": "NOT READY", "WAIT": "RECOMMENDED", "NO_TRADE": "VALID ALTERNATIVE"})
        self.assertTrue(all("valid" not in option for option in display["decision_options"]))
        self.assertEqual(display["decision_quality_score"]["overall_score"], 4)
        self.assertEqual(display["executed_trade_verdict"]["outcome_status"], "PROFITABLE")
        self.assertEqual(display["executed_trade_verdict"]["plan_standard_status"], "BELOW_REQUIRED_RR")
        self.assertNotIn("overall_rating", display["executed_trade_verdict"])
        self.assertNotIn("Break-even / recovery", [row["component"] for row in display["executed_trade_verdict"]["rows"]])

    def test_short_planned_risk_and_reward_use_short_direction(self):
        analysis = ReplayCoachAnalysis.model_validate({"executed_trade_analysis": {"summary": "x", "good": [], "bad": [], "how_to_improve": []}, "alternative_trade_plans": [], "key_learning": {"lesson": "x", "numeric_rule": "x", "example_using_this_trade": "x"}, "limitations": []})
        context = {"executed_trade": {"side": "SELL", "entry_price": 100, "entry_timestamp": "2026-09-22T10:08:00+05:30", "pnl_amount": -10, "quantity": 3}, "documented_plan": {"position_type": "SHORT"}, "decision_context": {"decision_timing": {"last_completed_stock_candle_time": "2026-09-22T10:00:00+05:30"}, "stock_direction": {}, "nifty_direction": {}, "stock_relative_volume": {}, "support_resistance": [], "risk_economics": {"entry": 100, "stop": 105, "target": 85, "required_ratio": 4.0, "take_valid": False}}}
        rows = ReplayCoachResponsePresenter.coach_display(analysis, context)["executed_trade_verdict"]["rows"]
        values = {row["component"]: row["value"] for row in rows}
        self.assertEqual(values["Planned risk"], "₹15.00")
        self.assertEqual(values["Planned reward"], "₹45.00")

    def test_option_statuses_are_resolved_by_decision_not_order(self):
        statuses = ReplayCoachService._decision_option_statuses([
            {"decision": "NO_TRADE", "status": "VALID ALTERNATIVE"},
            {"decision": "TAKE", "status": "NOT READY"},
            {"decision": "WAIT", "status": "RECOMMENDED"},
        ])
        self.assertEqual(statuses["TAKE"], "NOT READY")
        self.assertEqual(statuses["WAIT"], "RECOMMENDED")
        self.assertEqual(statuses["NO_TRADE"], "VALID ALTERNATIVE")

    def test_missing_take_status_is_controlled_contract_error(self):
        with self.assertRaises(ValueError):
            ReplayCoachService._decision_option_statuses([
                {"decision": "WAIT", "status": "RECOMMENDED"},
                {"decision": "NO_TRADE", "status": "VALID ALTERNATIVE"},
            ])
