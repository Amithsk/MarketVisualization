"""Replay Coach orchestration and temporary session storage."""
import hashlib
import json
import os
from typing import Any, Dict
from uuid import uuid4

from backend.services.replay_coach_openai_service import (
    ReplayCoachError, ReplayCoachResponseError,
    ReplayCoachOpenAIService,
)
from backend.models.replay_coach_model import ReplayCoachAnalysis
from backend.repositories.replay_coach_repository import ReplayCoachRepository


class ReplayCoachSessionStore:
    """Temporary in-memory store; contents are lost when this backend restarts."""
    _sessions: Dict[str, Dict[str, str]] = {}

    @classmethod
    def create(cls, trade_date: str, stock: str, response_id: str) -> str:
        session_id = str(uuid4())
        cls._sessions[session_id] = {"trade_date": trade_date, "stock": stock, "openai_response_id": response_id}
        return session_id


class ReplayCoachService:
    STALE_PROCESSING_SECONDS = 180.0

    @classmethod
    def identity(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        canonical = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
        return {
            "trade_id": context["executed_trade"]["trade_id"],
            "trade_date": context["trade_date"],
            "normalized_symbol": context["stock"]["symbol"].strip().upper().removeprefix("NSE:"),
            "context_version": context.get("context_version", "replay_coach_v1"),
            "evidence_hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "prompt_version": ReplayCoachOpenAIService.PROMPT_VERSION,
            "coach_schema_version": ReplayCoachOpenAIService.COACH_SCHEMA_VERSION,
            "requested_model": ReplayCoachOpenAIService.requested_model(),
            "evidence_json": canonical,
        }

    @classmethod
    def start(cls, context: Dict[str, Any], db=None, repository=ReplayCoachRepository) -> Dict[str, Any]:
        # db=None retains the existing isolated service-test seam; production always supplies a session.
        if db is None:
            result = cls._generate(context)
            result.pop("_usage", None)
            result.pop("_persisted_analysis", None)
            return result
        identity = cls.identity(context)
        prefix = identity["evidence_hash"][:12]
        record, claimed = repository.claim(db, identity, cls._stale_processing_seconds())
        if record and record["status"] == "COMPLETED":
            try:
                payload = record["analysis_json"]
                if isinstance(payload, str): payload = json.loads(payload)
                analysis = ReplayCoachAnalysis.model_validate(payload)
            except Exception as error:
                print(f"Replay Coach stored analysis invalid: analysis_id={record['id']} evidence_hash_prefix={prefix} error_type={type(error).__name__}")
                raise ReplayCoachResponseError() from error
            print(f"Replay Coach stored analysis reused: trade_date={identity['trade_date']} symbol={identity['normalized_symbol']} analysis_id={record['id']} evidence_hash_prefix={prefix} provider_called=False")
            return cls._result(context, analysis, record.get("provider_response_id"), {"model": record.get("actual_model")}, "stored", record)
        if not claimed:
            print(f"Replay Coach concurrent request suppressed: trade_date={identity['trade_date']} symbol={identity['normalized_symbol']} evidence_hash_prefix={prefix}")
            raise ReplayCoachInProgressError()
        print(f"Replay Coach claim won: trade_date={identity['trade_date']} symbol={identity['normalized_symbol']} analysis_id={record['id']} evidence_hash_prefix={prefix}")
        try:
            result = cls._generate(context)
            repository.complete(db, record["id"], result.pop("_persisted_analysis"), result["openai_response_id"], result.pop("_usage"))
            print(f"Replay Coach record completed: analysis_id={record['id']} evidence_hash_prefix={prefix}")
            result.update({"result_source": "generated", "reused": False, "analysis_id": record["id"], "model": result.get("model")})
            return result
        except Exception as error:
            try:
                repository.fail(db, record["id"], getattr(error, "code", "REPLAY_COACH_FAILED"))
                print(f"Replay Coach record failed: analysis_id={record['id']} evidence_hash_prefix={prefix} reason={getattr(error, 'code', 'REPLAY_COACH_FAILED')}")
            except Exception as persistence_error:
                print(f"Replay Coach persistence failure: analysis_id={record['id']} error_type={type(persistence_error).__name__}")
            raise

    @classmethod
    def _generate(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        analysis, response_id, _usage = ReplayCoachOpenAIService.analyze(context)
        return cls._result(context, analysis, response_id, _usage, "generated") | {
            "_usage": _usage,
            "_persisted_analysis": analysis.model_dump(mode="json", exclude_computed_fields=True),
        }

    @classmethod
    def _result(cls, context: Dict[str, Any], analysis: ReplayCoachAnalysis, response_id: str, usage: Dict[str, Any], source: str, record=None) -> Dict[str, Any]:
        session_id = ReplayCoachSessionStore.create(context["trade_date"], context["stock"]["symbol"], response_id or "stored")
        try:
            serialized_analysis = analysis.model_dump(mode="json")
        except Exception as error:
            print(f"Replay Coach response diagnostic: reason=RESPONSE_SERIALIZATION_FAILED error_type={type(error).__name__}")
            raise ReplayCoachResponseError() from error
        result = {"coach_session_id": session_id, "openai_response_id": response_id, "analysis": serialized_analysis}
        if record is not None:
            result.update({"result_source": source, "reused": source == "stored", "analysis_id": record["id"], "generated_at": str(record.get("completed_at")), "model": usage.get("model")})
        return result

    @classmethod
    def _stale_processing_seconds(cls) -> float:
        try: return max(float(os.getenv("OPENAI_REPLAY_COACH_STALE_PROCESSING_SECONDS", "180")), 180.0)
        except ValueError: return cls.STALE_PROCESSING_SECONDS


class ReplayCoachInProgressError(ReplayCoachError):
    code, status_code, public_message = "REPLAY_COACH_IN_PROGRESS", 409, "Replay Coach analysis is already in progress."
