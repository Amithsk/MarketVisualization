"""Compact, provider-only projection of canonical Replay Coach evidence.

The canonical context remains the persistence and follow-up source of truth.
This projection removes presentation-only and duplicated derived sections while
retaining every stock and market candle in a lossless column/row form.
"""
from typing import Any


CANDLE_COLUMNS = ("time", "open", "high", "low", "close", "volume", "vwap")


class ReplayCoachProviderContext:
    VERSION = "replay_coach_provider_context_v1"

    @classmethod
    def build(cls, canonical: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider_context_version": cls.VERSION,
            "trade_date": canonical.get("trade_date"),
            "timezone": canonical.get("timezone"),
            "candle_interval_minutes": canonical.get("candle_interval_minutes"),
            "executed_trade": canonical.get("executed_trade", {}),
            "execution_history": canonical.get("execution_history", []),
            "documented_plan": canonical.get("documented_plan", {}),
            # Decision context is the single authoritative representation of
            # deterministic market facts; coaching_facts is a prose-oriented
            # duplicate and active_trade_candle_review is frontend-only.
            "decision_context": canonical.get("decision_context", {}),
            "data_quality": canonical.get("data_quality", {}),
            "stock": cls._candles(canonical.get("stock", {})),
            "market": cls._candles(canonical.get("market", {})),
        }

    @staticmethod
    def _candles(section: dict[str, Any]) -> dict[str, Any]:
        candles = section.get("candles", []) if isinstance(section, dict) else []
        return {
            "symbol": section.get("symbol") if isinstance(section, dict) else None,
            "timestamp_semantics": "CANDLE_OPEN",
            "columns": list(CANDLE_COLUMNS),
            "rows": [[candle.get(column) for column in CANDLE_COLUMNS] for candle in candles if isinstance(candle, dict)],
        }

