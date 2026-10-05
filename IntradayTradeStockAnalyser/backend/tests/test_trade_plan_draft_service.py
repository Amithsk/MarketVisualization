import unittest

from backend.services.trade_plan_draft_service import TradePlanDraftService


def candle(time, open_, close, volume=100):
    return {"time": time, "open": open_, "high": max(open_, close) + 1, "low": min(open_, close) - 1, "close": close, "volume": volume}


def request(direction="LONG", strategy="ORB Breakout", stock=None, nifty=None, **values):
    return {
        "direction": direction,
        "strategy": strategy,
        "context_timestamp": "2026-09-22T09:45:00+05:30",
        "stock_candles": stock if stock is not None else [candle(f"2026-09-22T09:{minute:02}:00+05:30", 100, 101, 100) for minute in (15, 20, 25, 30, 35, 40, 45)],
        "nifty_candles": nifty if nifty is not None else [candle(f"2026-09-22T09:{minute:02}:00+05:30", 200, 199, 100) for minute in (15, 20, 25, 30, 35, 40, 45)],
        "entry": "102.50", "stop_loss": "99.50", "target": "108.50",
        "invalidation": "the support breaks on a completed candle",
        "entry_confirmation": "a completed candle closes above resistance",
        **values,
    }


class TradePlanDraftServiceTests(unittest.TestCase):
    def test_long_orb_draft_reuses_prices_and_completed_evidence(self):
        result = TradePlanDraftService.build(request())
        text = result["draft"]
        self.assertIn("BUY", text)
        self.assertIn("opening-range high", text)
        self.assertIn("102.50", text)
        self.assertIn("99.50", text)
        self.assertIn("108.50", text)
        self.assertIn("outperforming NIFTY", text)

    def test_short_template_and_weak_volume_are_honest(self):
        stock = [candle(f"2026-09-22T09:{minute:02}:00+05:30", 100, 99, 100) for minute in (15, 20, 25, 30, 35, 40, 45)]
        nifty = [candle(f"2026-09-22T09:{minute:02}:00+05:30", 200, 201, 100) for minute in (15, 20, 25, 30, 35, 40, 45)]
        text = TradePlanDraftService.build(request("SHORT", "ORB Breakdown", stock, nifty))["draft"]
        self.assertIn("SELL", text)
        self.assertIn("opening-range low", text)
        self.assertIn("not expanded", text)
        self.assertIn("underperforming NIFTY", text)

    def test_short_vwap_rejection_describes_lower_continuation(self):
        text = TradePlanDraftService.build(request("SHORT", "VWAP Rejection"))["draft"]

        self.assertIn("price rejecting VWAP and continuing lower", text)
        self.assertNotIn("opening-range high", text)

    def test_missing_context_uses_editable_placeholders_and_excludes_future_candle(self):
        stock = [candle("2026-09-22T09:45:00+05:30", 100, 100, 100), candle("2026-09-22T09:50:00+05:30", 100, 999, 10000)]
        text = TradePlanDraftService.build(request(stock=stock, nifty=[], invalidation="", entry_confirmation=""))["draft"]
        self.assertIn("[NIFTY condition unavailable]", text)
        self.assertIn("[entry confirmation]", text)
        self.assertIn("[invalidation condition]", text)
        self.assertNotIn("999", text)
