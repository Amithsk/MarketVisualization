import json
import os
import asyncio
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from pydantic import ValidationError

from backend.models.replay_coach_model import ReplayCoachAnalysis
from backend.services.replay_coach_service import (
    ReplayCoachConfigurationError, ReplayCoachResponseError, ReplayCoachService,
    ReplayCoachSessionStore, ReplayCoachTimeoutError,
)
from backend.api.replay import start_replay_coach


def context():
    return {
        "trade_date": "2026-09-16", "stock": {"symbol": "BHARTIARTL", "candles": [{"time": "2026-09-16T09:15:00+05:30"}]},
        "market": {"symbol": "NIFTY_FUTURES", "candles": [{"time": "2026-09-16T09:15:00+05:30"}]},
        "executed_trade": {"trade_id": 152, "entry_price": 100, "entry_timestamp": "2026-09-16T09:15:00+05:30"},
        "data_quality": {"market_vwap_available": False},
    }


def analysis(side="BUY"):
    entry, stop, target = (100, 99, 102) if side == "BUY" else (100, 101, 98)
    return {
        "executed_trade_analysis": {"summary": "Reviewed", "good": [], "bad": [], "how_to_improve": []},
        "alternative_trade_plans": [
            {"name": "Action", "decision": "TAKE", "side": side, "entry_condition": "Evidence", "entry_price": entry, "stop_price": stop, "target_price": target, "risk": 1, "reward": 2, "risk_reward_ratio": 2, "rating": 7, "why_good": ["Evidence"], "risks": ["Risk"], "evidence_times": ["2026-09-16T09:15:00+05:30"]},
            {"name": "Wait", "decision": "WAIT", "side": None, "entry_condition": "Wait", "entry_price": None, "stop_price": None, "target_price": None, "risk": None, "reward": None, "risk_reward_ratio": None, "rating": 5, "why_good": ["Patience"], "risks": ["Miss"], "evidence_times": []},
            {"name": "No-trade plan", "decision": "NO_TRADE", "side": None, "entry_condition": "No trade", "entry_price": None, "stop_price": None, "target_price": None, "risk": None, "reward": None, "risk_reward_ratio": None, "rating": 4, "why_good": ["Safety"], "risks": ["Opportunity"], "evidence_times": []},
        ],
        "key_learning": {"lesson": "Lesson", "numeric_rule": "Rule", "example_using_this_trade": "Example"}, "limitations": ["NIFTY VWAP unavailable"],
    }


class FakeResponses:
    def __init__(self, payload): self.payload, self.calls = payload, []
    def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.payload, Exception): raise self.payload
        return SimpleNamespace(id="resp_123", output_text=json.dumps(self.payload))


class ReplayCoachServiceTests(TestCase):
    def setUp(self): ReplayCoachSessionStore._sessions.clear()

    def test_valid_context_calls_openai_once_with_only_context_and_retains_response_id(self):
        responses = FakeResponses(analysis())
        client = SimpleNamespace(responses=responses)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False), patch.object(ReplayCoachService, "_client", return_value=client):
            result = ReplayCoachService.start(context())
        self.assertEqual(len(responses.calls), 1)
        sent = json.loads(responses.calls[0]["input"][1]["content"])
        self.assertEqual(sent, context())
        self.assertIn("stock", sent); self.assertIn("market", sent); self.assertIn("executed_trade", sent)
        self.assertNotIn("trade_data", sent); self.assertNotIn("narrative_context", sent); self.assertNotIn("explanation_context", sent)
        self.assertEqual(ReplayCoachSessionStore._sessions[result["coach_session_id"]]["openai_response_id"], "resp_123")
        self.assertEqual(result["analysis"], analysis())

    def test_missing_key_does_not_create_client(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(ReplayCoachService, "_client") as client:
            with self.assertRaises(ReplayCoachConfigurationError): ReplayCoachService.analyze(context())
        client.assert_not_called()

    def test_timeout_and_invalid_output_are_safe_errors(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False), patch.object(ReplayCoachService, "_client", return_value=SimpleNamespace(responses=FakeResponses(TimeoutError()))):
            with self.assertRaises(ReplayCoachTimeoutError): ReplayCoachService.analyze(context())
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False), patch.object(ReplayCoachService, "_client", return_value=SimpleNamespace(responses=FakeResponses({}))):
            with self.assertRaises(ReplayCoachResponseError): ReplayCoachService.analyze(context())

    def test_buy_and_sell_risk_reward_are_validated(self):
        ReplayCoachAnalysis.model_validate(analysis("BUY"))
        ReplayCoachAnalysis.model_validate(analysis("SELL"))
        invalid = analysis("BUY"); invalid["alternative_trade_plans"][0]["risk"] = 2
        with self.assertRaises(ValidationError): ReplayCoachAnalysis.model_validate(invalid)

    def test_invalid_context_never_starts_openai_coach(self):
        invalid_replay = {"executed_trade": None, "stock_candles": [], "nifty_candles": []}
        with patch("backend.api.replay.ReplayService.get_replay_data", return_value=invalid_replay), patch("backend.api.replay.ReplayCoachService.start") as start:
            response = asyncio.run(start_replay_coach("2026-09-16", "BHARTIARTL", db=None))
        self.assertEqual(response.status_code, 422)
        start.assert_not_called()
