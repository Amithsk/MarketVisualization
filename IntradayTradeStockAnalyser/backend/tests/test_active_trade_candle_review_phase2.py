from unittest import TestCase
from backend.services.active_trade_candle_review_service import ActiveTradeCandleReviewService


def candle(time, close=100):
    return {"time": time, "open": close, "high": close + 1, "low": close - 1, "close": close}


class ActiveTradeCandleReviewPhase2Tests(TestCase):
    def test_bharti_same_candle_adds_keep_order_and_weighted_average(self):
        events = [
            {"sequence": 1, "event_type": "ENTRY", "quantity": 50, "price": 2050.4, "execution_timestamp": "2026-11-09T14:04:29", "open_quantity_before": 0, "open_quantity_after": 50, "weighted_average_after": 2050.4, "realized_gross_pnl": 0},
            {"sequence": 2, "event_type": "ADD", "quantity": 50, "price": 2062, "execution_timestamp": "2026-11-09T14:07:22", "open_quantity_before": 50, "open_quantity_after": 100, "weighted_average_after": 2056.2, "realized_gross_pnl": 0},
            {"sequence": 3, "event_type": "ADD", "quantity": 50, "price": 2062, "execution_timestamp": "2026-11-09T14:09:58", "open_quantity_before": 100, "open_quantity_after": 150, "weighted_average_after": 2058.133333, "realized_gross_pnl": 0},
            {"sequence": 4, "event_type": "EXIT", "quantity": 150, "price": 2060, "execution_timestamp": "2026-11-09T14:20:00", "open_quantity_before": 150, "open_quantity_after": 0, "weighted_average_after": None, "realized_gross_pnl": -280, "cumulative_realized_gross_pnl": -280},
        ]
        result = ActiveTradeCandleReviewService.build([candle("2026-11-09T14:00:00", 2055), candle("2026-11-09T14:05:00", 2057), candle("2026-11-09T14:10:00", 2058), candle("2026-11-09T14:15:00", 2059)], [], {"side":"SELL"}, {"position_type":"SHORT"}, events)
        row = next(item for item in result["items"] if item["completion_time"].startswith("2026-11-09T14:10"))
        before_adds = next(item for item in result["items"] if item["completion_time"].startswith("2026-11-09T14:05"))
        self.assertEqual(before_adds["trade_effect"]["basis_price"], 2050.4)  # later fills are excluded
        self.assertEqual(row["trade_effect"]["open_quantity"], 150)
        self.assertAlmostEqual(row["trade_effect"]["basis_price"], 2058.133333)
        self.assertEqual(row["trade_effect"]["basis_source"], "RECONSTRUCTED_EXECUTION_HISTORY")
        self.assertEqual(len(row["trade_effect"]["execution_details"]), 2)

    def test_partial_exit_readd_retains_realized_pnl_and_final_exit_boundary(self):
        events = [
            {"event_type":"ENTRY","quantity":100,"price":102,"execution_timestamp":"2026-11-09T10:00:00","open_quantity_before":0,"open_quantity_after":100,"weighted_average_after":102,"realized_gross_pnl":0},
            {"event_type":"EXIT","quantity":40,"price":101,"execution_timestamp":"2026-11-09T10:06:00","open_quantity_before":100,"open_quantity_after":60,"weighted_average_after":102,"realized_gross_pnl":40},
            {"event_type":"ADD","quantity":40,"price":106,"execution_timestamp":"2026-11-09T10:08:00","open_quantity_before":60,"open_quantity_after":100,"weighted_average_after":103.6,"realized_gross_pnl":0},
            {"event_type":"EXIT","quantity":100,"price":105,"execution_timestamp":"2026-11-09T10:15:00","open_quantity_before":100,"open_quantity_after":0,"weighted_average_after":None,"realized_gross_pnl":-140},
        ]
        result = ActiveTradeCandleReviewService.build([candle("2026-11-09T10:00:00",103),candle("2026-11-09T10:05:00",104),candle("2026-11-09T10:10:00",105)], [], {"side":"SELL"}, {"position_type":"SHORT"}, events)
        row = next(item for item in result["items"] if item["completion_time"].startswith("2026-11-09T10:10"))
        self.assertEqual(row["trade_effect"]["open_quantity"],100)
        self.assertAlmostEqual(row["trade_effect"]["basis_price"],103.6)
        self.assertEqual(row["trade_effect"]["realized_gross_pnl"],40)
        self.assertEqual(result["final_exit"]["timestamp"],"2026-11-09T10:15:00")

    def test_boundary_fill_is_counted_once_in_next_candle_and_missing_nifty_is_explicit(self):
        events = [
            {"sequence":1,"event_type":"ENTRY","quantity":10,"price":100,"execution_timestamp":"2026-11-09T10:00:00","open_quantity_before":0,"open_quantity_after":10,"weighted_average_after":100,"realized_gross_pnl":0},
            {"sequence":2,"event_type":"EXIT","quantity":10,"price":101,"execution_timestamp":"2026-11-09T10:10:00","open_quantity_before":10,"open_quantity_after":0,"weighted_average_after":None,"realized_gross_pnl":10},
        ]
        result = ActiveTradeCandleReviewService.build([candle("2026-11-09T10:00:00"), candle("2026-11-09T10:05:00")], [], {"side":"BUY"}, {"position_type":"LONG"}, events)
        self.assertEqual(result["items"][0]["completion_time"], "2026-11-09T10:05:00")
        self.assertEqual(result["items"][0]["trade_effect"]["open_quantity"], 10)
        self.assertIn("unavailable", result["items"][0]["nifty_relationship"]["message"].lower())
        self.assertIn("[start, end)", result["timestamp_semantics"])

    def test_intrabar_exit_excludes_exit_candle_and_legacy_entry_uses_summary(self):
        intrabar = ActiveTradeCandleReviewService.build([candle("2026-11-09T10:00:00"), candle("2026-11-09T10:05:00")], [], {"side":"BUY"}, {"position_type":"LONG"}, [{"event_type":"ENTRY","quantity":10,"price":100,"execution_timestamp":"2026-11-09T10:00:01","open_quantity_before":0,"open_quantity_after":10,"weighted_average_after":100},{"event_type":"EXIT","quantity":10,"price":101,"execution_timestamp":"2026-11-09T10:07:00","open_quantity_before":10,"open_quantity_after":0,"weighted_average_after":None,"realized_gross_pnl":10}])
        # The entry candle completed while open; the 10:05 candle is excluded
        # because the final exit occurred inside it.
        self.assertEqual(intrabar["summary"]["eligible_completed_candles"], 1)
        self.assertEqual(intrabar["final_exit"]["price"], 101)
        legacy = ActiveTradeCandleReviewService.build([candle("2026-11-09T10:00:00"), candle("2026-11-09T10:05:00")], [], {"side":"BUY","quantity":10,"entry_price":100,"entry_timestamp":"2026-11-09T10:00:00","exit_timestamp":"2026-11-09T10:10:00"}, {"position_type":"LONG"})
        self.assertEqual(legacy["summary"]["eligible_completed_candles"], 2)

    def test_trade_effect_direction_rounding_and_unavailable_contract(self):
        state={"open_quantity":50,"weighted_average":1319.50}
        short = ActiveTradeCandleReviewService._effect(candle("2026-11-09T10:00:00",1319.20), "SHORT", state, [], "ORIGINAL_EXECUTED_ENTRY")
        self.assertEqual((short["movement_per_share_signed"], short["movement_classification"], short["gross_unrealized_pnl"]), (.3, "FAVOURABLE", 15.0))
        long = ActiveTradeCandleReviewService._effect(candle("2026-11-09T10:00:00",1319.20), "LONG", state, [], "ORIGINAL_EXECUTED_ENTRY")
        self.assertEqual(long["movement_classification"], "ADVERSE")
        rounded = ActiveTradeCandleReviewService._effect(candle("2026-11-09T10:00:00",100.005), "LONG", {"open_quantity":3,"weighted_average":100}, [], "ORIGINAL_EXECUTED_ENTRY")
        self.assertEqual((rounded["movement_per_share_signed"], rounded["gross_unrealized_pnl"]), (.01, .03))
        unavailable = ActiveTradeCandleReviewService._effect(candle("2026-11-09T10:00:00"), "LONG", {"open_quantity":10,"weighted_average":None}, [], "UNAVAILABLE")
        self.assertEqual(unavailable["movement_classification"], "UNAVAILABLE")
        self.assertNotIn("target", short["message"].lower())

    def test_decisions_are_evidence_specific_and_target_stop_math_is_directional(self):
        effect={"movement_classification":"FAVOURABLE","movement_per_share_signed":.3}
        hold=ActiveTradeCandleReviewService._decision("SHORT", {"open":101,"high":101,"low":99,"close":99}, "LH_LL", effect, 105, 98, False)
        watch=ActiveTradeCandleReviewService._decision("SHORT", {"open":101,"high":102,"low":100,"close":101}, "MIXED", effect, 105, 98, False)
        short_target=ActiveTradeCandleReviewService._decision("SHORT", {"open":101,"high":101,"low":97.7,"close":99}, "LH_LL", effect, 105, 98, False)
        long_target=ActiveTradeCandleReviewService._decision("LONG", {"open":101,"high":102.3,"low":100,"close":101}, "HH_HL", effect, 99, 102, False)
        short_stop=ActiveTradeCandleReviewService._decision("SHORT", {"open":101,"high":105.4,"low":100,"close":101}, "LH_LL", effect, 105, 98, False)
        long_stop=ActiveTradeCandleReviewService._decision("LONG", {"open":101,"high":102,"low":98.6,"close":101}, "HH_HL", effect, 99, 103, False)
        self.assertEqual((hold["classification"],watch["classification"],short_target["classification"]), ("HOLD","WATCH","EXIT"))
        self.assertIn("0.30", short_target["message"]); self.assertIn("0.30", long_target["message"])
        self.assertIn("0.40", short_stop["message"]); self.assertIn("0.40", long_stop["message"])
        self.assertNotIn("Coach assessment at candle close", hold["message"])

    def test_exit_is_terminal_compares_actual_exit_and_entry_candle_is_ambiguous(self):
        events=[{"event_type":"ENTRY","quantity":10,"price":100,"execution_timestamp":"2026-11-09T10:00:01","open_quantity_before":0,"open_quantity_after":10,"weighted_average_after":100},{"event_type":"EXIT","quantity":10,"price":99,"execution_timestamp":"2026-11-09T10:17:00","open_quantity_before":10,"open_quantity_after":0,"weighted_average_after":None}]
        result=ActiveTradeCandleReviewService.build([candle("2026-11-09T10:00:00",101),candle("2026-11-09T10:05:00",99),candle("2026-11-09T10:10:00",99)], [], {"side":"SELL"}, {"position_type":"SHORT","target_price":100}, events)
        # First candle could have hit its target before the 10:00:01 entry.
        self.assertEqual(result["items"][0]["decision"]["reason_codes"], ["INTRABAR_SEQUENCE_UNKNOWN"])
        self.assertEqual(result["items"][1]["decision"]["classification"], "EXIT")
        self.assertEqual(len(result["items"]), 2)
        self.assertIn("actual Journal exit", result["coach_exit_signal"]["message"])
