import unittest

from backend.services.replay_coach_adapter import _evidence_times


class ReplayCoachAdapterTests(unittest.TestCase):
    def test_unsupported_optional_evidence_time_is_discarded(self):
        self.assertEqual(_evidence_times("2026-09-23T10:08:00+05:30", {"2026-09-23T10:00:00+05:30"}), [])

    def test_invalid_optional_evidence_time_is_discarded(self):
        self.assertEqual(_evidence_times("not-a-time", {"2026-09-23T10:00:00+05:30"}), [])

    def test_supported_optional_evidence_time_is_retained(self):
        value = "2026-09-23T10:00:00+05:30"
        self.assertEqual(_evidence_times(value, {value}), [value])
