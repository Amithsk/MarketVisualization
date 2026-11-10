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
        self.assertEqual(row["trade_effect"]["open_quantity"], 150)
        self.assertAlmostEqual(row["trade_effect"]["weighted_average"], 2058.133333)
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
        self.assertAlmostEqual(row["trade_effect"]["weighted_average"],103.6)
        self.assertEqual(row["trade_effect"]["realized_gross_pnl"],40)
        self.assertEqual(result["final_exit"]["timestamp"],"2026-11-09T10:15:00")
