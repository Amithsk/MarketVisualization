import threading
import time
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import MagicMock, patch

import httpx

from backend.services.live_service import (
    LiveService,
    NIFTY_CONNECT_TIMEOUT_SECONDS,
    NIFTY_READ_TIMEOUT_SECONDS,
)


class _DelayedNiftyHandler(BaseHTTPRequestHandler):
    delay_seconds = 0.0

    def do_GET(self):
        time.sleep(self.delay_seconds)
        body = b'{"candles": [], "trade_date": "2026-11-23"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


@contextmanager
def delayed_nifty_server(delay_seconds):
    handler = type("DelayedNiftyHandler", (_DelayedNiftyHandler,), {
        "delay_seconds": delay_seconds,
    })
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class LiveServiceTimeoutTests(unittest.TestCase):
    def test_nifty_request_accepts_a_16_second_response(self):
        with delayed_nifty_server(16.0) as base_url, patch(
            "backend.services.live_service.BASE_URL", base_url
        ):
            started = time.monotonic()
            result = LiveService.get_nifty_candles()

        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(time.monotonic() - started, 16.0)

    def test_nifty_request_times_out_after_30_second_read_limit(self):
        with delayed_nifty_server(31.0) as base_url, patch(
            "backend.services.live_service.BASE_URL", base_url
        ):
            started = time.monotonic()
            result = LiveService.get_nifty_candles()
            elapsed = time.monotonic() - started

        self.assertEqual(result["status"], "error")
        self.assertIn("timed out", result["message"].lower())
        self.assertGreaterEqual(elapsed, NIFTY_READ_TIMEOUT_SECONDS)
        self.assertLess(elapsed, 31.0)

    def test_stock_timeout_remains_10_seconds(self):
        response = MagicMock()
        response.json.return_value = {"candles": []}
        response.raise_for_status.return_value = None

        with patch("backend.services.live_service.httpx.Client") as client_class:
            client = client_class.return_value.__enter__.return_value
            client.get.return_value = response
            result = LiveService.get_symbol_candles("INFY")

        self.assertEqual(result["status"], "success")
        self.assertEqual(client_class.call_args.kwargs["timeout"], 10.0)

    def test_nifty_timeout_values_are_explicit(self):
        with patch("backend.services.live_service.httpx.get") as get:
            response = get.return_value
            response.json.return_value = {"candles": []}
            response.raise_for_status.return_value = None
            LiveService.get_nifty_candles()

        timeout = get.call_args.kwargs["timeout"]
        self.assertEqual(timeout.connect, NIFTY_CONNECT_TIMEOUT_SECONDS)
        self.assertEqual(timeout.read, NIFTY_READ_TIMEOUT_SECONDS)


if __name__ == "__main__":
    unittest.main()
