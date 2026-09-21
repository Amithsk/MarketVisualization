"""Replay Coach orchestration and temporary session storage."""
from typing import Any, Dict
from uuid import uuid4

from backend.services.replay_coach_openai_service import (
    ReplayCoachError, ReplayCoachResponseError,
    ReplayCoachOpenAIService,
)


class ReplayCoachSessionStore:
    """Temporary in-memory store; contents are lost when this backend restarts."""
    _sessions: Dict[str, Dict[str, str]] = {}

    @classmethod
    def create(cls, trade_date: str, stock: str, response_id: str) -> str:
        session_id = str(uuid4())
        cls._sessions[session_id] = {"trade_date": trade_date, "stock": stock, "openai_response_id": response_id}
        return session_id


class ReplayCoachService:
    @classmethod
    def start(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        analysis, response_id, _usage = ReplayCoachOpenAIService.analyze(context)
        session_id = ReplayCoachSessionStore.create(context["trade_date"], context["stock"]["symbol"], response_id)
        try:
            serialized_analysis = analysis.model_dump(mode="json")
        except Exception as error:
            print(f"Replay Coach response diagnostic: reason=RESPONSE_SERIALIZATION_FAILED error_type={type(error).__name__}")
            raise ReplayCoachResponseError() from error
        return {"coach_session_id": session_id, "openai_response_id": response_id, "analysis": serialized_analysis}
