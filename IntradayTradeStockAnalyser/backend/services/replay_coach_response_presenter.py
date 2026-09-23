"""Present canonical Replay Coach analysis safely for the public API."""
from copy import deepcopy
from datetime import datetime
import re
from typing import Any
from zoneinfo import ZoneInfo

from backend.models.replay_coach_model import ReplayCoachAnalysis


IST = ZoneInfo("Asia/Kolkata")
# Complete ISO datetimes only.  This deliberately excludes plain clock times,
# dates, prices, ratios, and partial timestamp-like values.
ISO_TIMESTAMP = re.compile(
    r"(?<![A-Za-z0-9_])\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})(?![A-Za-z0-9_])"
)


class ReplayCoachResponsePresenter:
    """Converts timestamps in response-only analysis content to IST HH:mm."""

    @classmethod
    def present(cls, analysis: ReplayCoachAnalysis) -> dict[str, Any]:
        """Return a display copy; never mutate the validated canonical model."""
        payload = deepcopy(analysis.model_dump(mode="json"))
        return cls._present_value(payload)

    @classmethod
    def _present_value(cls, value: Any, field_name: str | None = None) -> Any:
        if isinstance(value, dict):
            return {key: cls._present_value(item, key) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._present_value(item, field_name) for item in value]
        if isinstance(value, str):
            if value == "documented_plan" and field_name in {"time", "evidence_times"}:
                return "Plan"
            return ISO_TIMESTAMP.sub(cls._format_timestamp, value)
        return value

    @staticmethod
    def _format_timestamp(match: re.Match[str]) -> str:
        raw = match.group(0)
        try:
            parsed = datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
            return parsed.astimezone(IST).strftime("%H:%M")
        except ValueError:
            # A syntactically timestamp-like but invalid value is retained.
            return raw
