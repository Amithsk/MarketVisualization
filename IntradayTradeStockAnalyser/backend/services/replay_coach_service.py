"""OpenAI-backed Replay Coach. Sessions intentionally live only in process memory."""
import json
import os
from typing import Any, Dict
from uuid import uuid4

import httpx
from pydantic import ValidationError

from backend.models.replay_coach_model import ReplayCoachAnalysis


class ReplayCoachError(Exception):
    code = "REPLAY_COACH_FAILED"
    status_code = 502
    public_message = "Replay Coach analysis is unavailable."


class ReplayCoachConfigurationError(ReplayCoachError):
    code, status_code, public_message = "OPENAI_NOT_CONFIGURED", 503, "Replay Coach is not configured."


class ReplayCoachTimeoutError(ReplayCoachError):
    code, status_code, public_message = "OPENAI_TIMEOUT", 504, "Replay Coach timed out."


class ReplayCoachProviderError(ReplayCoachError):
    code, status_code, public_message = "OPENAI_API_FAILED", 502, "Replay Coach provider request failed."


class ReplayCoachResponseError(ReplayCoachError):
    code, status_code, public_message = "INVALID_COACH_RESPONSE", 502, "Replay Coach returned an invalid analysis."


class ReplayCoachSessionStore:
    """Temporary in-memory store; contents are lost when this backend restarts."""
    _sessions: Dict[str, Dict[str, str]] = {}

    @classmethod
    def create(cls, trade_date: str, stock: str, response_id: str) -> str:
        session_id = str(uuid4())
        cls._sessions[session_id] = {"trade_date": trade_date, "stock": stock, "openai_response_id": response_id}
        return session_id


class ReplayCoachService:
    DEFAULT_MODEL = "gpt-4.1-mini"
    TIMEOUT_SECONDS = 45.0
    SYSTEM_INSTRUCTIONS = """You are a rigorous intraday Trade Replay Coach. Analyze only the supplied executed trade and candle evidence. Use whole-session stock and NIFTY Futures candles, but distinguish information knowable at a decision time from later outcomes. Every important conclusion needs candle timestamps and numeric evidence. Never invent VWAP, indicators, support, or resistance. NIFTY VWAP is unavailable unless supplied. Volume comparisons must state their calculation. Alternative plans are retrospective learning examples, not guarantees. Return only JSON conforming to the supplied schema."""

    @classmethod
    def analyze(cls, context: Dict[str, Any]) -> tuple[ReplayCoachAnalysis, str]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ReplayCoachConfigurationError()
        try:
            client = cls._client(api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_REPLAY_COACH_MODEL", cls.DEFAULT_MODEL),
                input=[
                    {"role": "developer", "content": cls.SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": json.dumps(context, default=str)},
                ],
                text={"format": {"type": "json_schema", "name": "replay_coach_analysis", "strict": True, "schema": cls._strict_schema()}},
            )
        except (TimeoutError, httpx.TimeoutException) as error:
            raise ReplayCoachTimeoutError() from error
        except ReplayCoachError:
            raise
        except Exception as error:
            if "timeout" in type(error).__name__.lower():
                raise ReplayCoachTimeoutError() from error
            raise ReplayCoachProviderError() from error
        try:
            analysis = ReplayCoachAnalysis.model_validate_json(response.output_text)
            response_id = response.id
            if not response_id:
                raise ValueError("missing response id")
            return analysis, response_id
        except (AttributeError, TypeError, ValueError, ValidationError) as error:
            raise ReplayCoachResponseError() from error

    @classmethod
    def start(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        analysis, response_id = cls.analyze(context)
        session_id = ReplayCoachSessionStore.create(context["trade_date"], context["stock"]["symbol"], response_id)
        return {"coach_session_id": session_id, "openai_response_id": response_id, "analysis": analysis.model_dump(mode="json")}

    @classmethod
    def _client(cls, api_key: str):
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ReplayCoachConfigurationError() from error
        return OpenAI(api_key=api_key, timeout=cls.TIMEOUT_SECONDS)

    @staticmethod
    def _strict_schema():
        """Structured Outputs requires every object property to be required.

        Nullable fields remain nullable through their existing ``anyOf`` definitions.
        """
        schema = ReplayCoachAnalysis.model_json_schema()

        def visit(value):
            if isinstance(value, dict):
                properties = value.get("properties")
                if isinstance(properties, dict):
                    value["required"] = list(properties)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(schema)
        return schema
