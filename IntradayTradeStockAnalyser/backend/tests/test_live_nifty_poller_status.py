import asyncio
from copy import deepcopy
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from backend.services.live_nifty_poller import LiveNiftyPoller
from backend.services.live_service import LiveService


class LiveNiftyPollerStatusTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.original_state = deepcopy(LiveNiftyPoller._state)
        self.original_refresh_lock = LiveNiftyPoller._refresh_lock
        self.original_state_lock = LiveNiftyPoller._state_lock
        LiveNiftyPoller._state = {
            "initialized": False,
            "payload": None,
            "trade_date": None,
            "last_refresh_time": None,
            "latest_candle_timestamp": None,
            "interval": None,
            "contract": None,
            "next_refresh_time": None,
            "last_error": None,
            "refresh_status": "no_data",
            "refresh_started_at": None,
            "last_successful_fetch_time": None,
        }
        LiveNiftyPoller._refresh_lock = asyncio.Lock()
        LiveNiftyPoller._state_lock = asyncio.Lock()

    async def asyncTearDown(self):
        LiveNiftyPoller._state = self.original_state
        LiveNiftyPoller._refresh_lock = self.original_refresh_lock
        LiveNiftyPoller._state_lock = self.original_state_lock

    async def test_success_and_failure_state_keep_last_successful_payload(self):
        success = {
            "status": "success",
            "trade_date": "2026-11-23",
            "interval": "5minute",
            "contract": "NIFTY-FUT",
            "candles": [{"time": "2026-11-23T10:00:00+05:30"}],
            "upstream_latest_candle_timestamp": "2026-11-23T10:05:00+05:30",
            "latest_completed_candle_timestamp": "2026-11-23T10:00:00+05:30",
            "market_context": {},
        }

        with patch.object(LiveNiftyPoller, "is_market_time", return_value=True), \
             patch.object(LiveNiftyPoller, "_current_trade_date", return_value="2026-11-23"), \
             patch.object(LiveService, "get_nifty_candles", return_value=success):
            await LiveNiftyPoller._refresh()

        updated = await LiveNiftyPoller.get_payload()
        self.assertEqual(updated["refresh_status"], "updated")
        self.assertIsNotNone(updated["refresh_started_at"])
        self.assertIsNotNone(updated["last_successful_fetch_time"])
        self.assertEqual(
            updated["latest_candle_timestamp"],
            "2026-11-23T10:00:00+05:30",
        )

        with patch.object(LiveNiftyPoller, "is_market_time", return_value=True), \
             patch.object(LiveNiftyPoller, "_current_trade_date", return_value="2026-11-23"), \
             patch.object(LiveService, "get_nifty_candles", return_value={
                 "status": "error", "message": "upstream unavailable"
             }):
            await LiveNiftyPoller._refresh()

        failed = await LiveNiftyPoller.get_payload()
        self.assertEqual(failed["refresh_status"], "failed")
        self.assertEqual(failed["last_error"], "upstream unavailable")
        self.assertEqual(failed["candles"], success["candles"])
        self.assertEqual(
            failed["last_successful_fetch_time"],
            updated["last_successful_fetch_time"],
        )

    async def test_no_data_response_exposes_initial_state(self):
        payload = await LiveNiftyPoller.get_payload()

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["refresh_status"], "no_data")
        self.assertIsNone(payload["last_successful_fetch_time"])
        self.assertIsNone(payload["latest_candle_timestamp"])
