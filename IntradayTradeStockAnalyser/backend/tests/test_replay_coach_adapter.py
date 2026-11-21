import unittest

from backend.models.replay_coach_provider_model import ProviderReplayCoachTransport
from backend.services.replay_coach_adapter import _required_evidence_time, to_application_analysis
from backend.services.replay_coach_openai_service import ReplayCoachOpenAIService


class ReplayCoachAdapterTests(unittest.TestCase):
    canonical = "2026-10-09T09:45:00+05:30"

    def test_prompt_requires_canonical_timestamps_for_structured_fields(self):
        instruction = "For `decision_time`, `decision_evidence_times`, and `outcome_evidence_times`, return exact supplied candle `time` strings verbatim in canonical ISO format."
        self.assertIn(instruction, ReplayCoachOpenAIService.SYSTEM_INSTRUCTIONS)

    def test_canonical_timestamp_matching_evidence_is_accepted(self):
        self.assertEqual(_required_evidence_time(self.canonical, {self.canonical}, "decision_evidence_times"), self.canonical)

    def test_human_readable_timestamp_is_rejected_for_structured_evidence(self):
        with self.assertRaisesRegex(ValueError, "decision_evidence_times contains an invalid timestamp"):
            _required_evidence_time("9:45 AM", {self.canonical}, "decision_evidence_times")

    def test_timestamp_not_present_in_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "decision_evidence_times must match a supplied stock or market candle timestamp"):
            _required_evidence_time("2026-10-09T09:50:00+05:30", {self.canonical}, "decision_evidence_times")

    def test_mocked_provider_response_with_canonical_timestamps_passes_adapter(self):
        provider = ProviderReplayCoachTransport.model_validate({
            "executed_trade_analysis": {"summary": "Evidence-only review.", "good": [], "bad": [], "how_to_improve": []},
            "best_full_session_plan": {
                "decision": "TAKE", "trade_name": "Breakout", "direction": "LONG", "opportunity_score": 8,
                "score_explanation": "Supported by the supplied candle.", "market_story": "The market supported the move.",
                "setup_explanation": "The stock broke above its range.", "decision_time": self.canonical,
                "entry_trigger": "Enter above 100.", "entry_price": 100.0, "entry_price_upper": None,
                "stop_price": 99.0, "target_price": 104.0, "invalidation_condition": "Close below 99.",
                "volume_explanation": "Volume expanded.", "nifty_explanation": "NIFTY was supportive.",
                "beginner_lesson": "Use completed candles.", "decision_evidence_times": [self.canonical],
                "outcome_evidence_times": [self.canonical],
            },
            "key_learning": {"lesson": "Wait for confirmation.", "numeric_rule": "Use the supplied level.", "example_using_this_trade": "The candle confirmed the breakout."},
            "limitations": [],
        })
        context = {"stock": {"candles": [{"time": self.canonical}]}, "market": {"candles": []}}
        analysis = to_application_analysis(provider, context)
        self.assertEqual(analysis.best_full_session_plan.decision_time, self.canonical)
        self.assertEqual(analysis.best_full_session_plan.decision_evidence_times, [self.canonical])
