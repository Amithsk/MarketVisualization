import unittest

from backend.services.replay_coach_adapter import _evidence_times
from backend.services.replay_coach_adapter import _required_evidence_time
from backend.services.replay_coach_adapter import _validated_evidence_times
from backend.services.replay_coach_adapter import _optional_decision_time


class ReplayCoachAdapterTests(unittest.TestCase):
    def test_unsupported_optional_evidence_time_is_discarded(self):
        self.assertEqual(_evidence_times("2026-09-23T10:08:00+05:30", {"2026-09-23T10:00:00+05:30"}), [])

    def test_invalid_optional_evidence_time_is_discarded(self):
        self.assertEqual(_evidence_times("not-a-time", {"2026-09-23T10:00:00+05:30"}), [])

    def test_supported_optional_evidence_time_is_retained(self):
        value = "2026-09-23T10:00:00+05:30"
        self.assertEqual(_evidence_times(value, {value}), [value])

    def test_unique_clock_evidence_time_resolves_to_the_supplied_timestamp(self):
        value = "2026-09-23T10:00:00+05:30"
        self.assertEqual(_required_evidence_time("10:00", {value}, "decision_evidence_times"), value)

    def test_unknown_clock_evidence_time_is_rejected(self):
        with self.assertRaises(ValueError):
            _required_evidence_time("10:05", {"2026-09-23T10:00:00+05:30"}, "decision_evidence_times")

    def test_equivalent_utc_timestamp_resolves_to_the_canonical_candle(self):
        canonical = "2026-09-23T10:00:00+05:30"
        self.assertEqual(_required_evidence_time("2026-09-23T04:30:00Z", {canonical}, "decision_evidence_times"), canonical)

    def test_naive_provider_timestamp_resolves_only_to_matching_session_candle(self):
        canonical = "2026-09-23T10:00:00+05:30"
        self.assertEqual(_required_evidence_time("2026-09-23T10:00:00", {canonical}, "decision_evidence_times"), canonical)

    def test_invalid_evidence_annotation_is_discarded(self):
        self.assertEqual(_validated_evidence_times(["10:05"], {"2026-09-23T10:00:00+05:30"}, "decision_evidence_times"), [])

    def test_invalid_decision_time_is_discarded_without_inventing_a_time(self):
        self.assertIsNone(_optional_decision_time("10:05", {"2026-09-23T10:00:00+05:30"}))
