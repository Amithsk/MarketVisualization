"""Replay Coach orchestration and temporary session storage."""
import hashlib
import json
import os
import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict
from uuid import uuid4

from backend.services.replay_coach_openai_service import (
    ReplayCoachError, ReplayCoachResponseError,
    ReplayCoachOpenAIService,
)
from backend.models.replay_coach_model import ReplayCoachAnalysis
from backend.repositories.replay_coach_repository import ReplayCoachRepository
from backend.services.replay_coach_response_presenter import ReplayCoachResponsePresenter
from backend.utils.database import SessionLocal


class ReplayCoachSessionStore:
    """Temporary in-memory store; contents are lost when this backend restarts."""
    _sessions: Dict[str, Dict[str, str]] = {}

    @classmethod
    def create(cls, trade_date: str, stock: str, response_id: str) -> str:
        session_id = str(uuid4())
        cls._sessions[session_id] = {"trade_date": trade_date, "stock": stock, "openai_response_id": response_id}
        return session_id

@dataclass
class ReplayCoachLifecycle:
    request_id: str
    analysis_id: int | None = None
    provider_call_attempted: bool = False
    provider_response_received: bool = False
    provider_response_id: str | None = None
    active_operation: str = "START"
    started_at: float = 0.0

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
    def start(cls, context: Dict[str, Any], db=None, repository=ReplayCoachRepository, session_factory=SessionLocal, request_id: str = "none", lifecycle=None) -> Dict[str, Any]:
        # db=None retains the existing isolated service-test seam; production always supplies a session.
        if db is None:
            result = cls._generate(context)
            result.pop("_usage", None)
            result.pop("_persisted_analysis", None)
            return result
        identity = cls.identity(context)
        logger = logging.getLogger(__name__)
        prefix = identity["evidence_hash"][:12]
        record, claimed = repository.claim(db, identity, cls._stale_processing_seconds(), request_id=request_id)
        if lifecycle is not None and record: lifecycle.analysis_id = record["id"]
        logger.info("Replay Coach record lookup: request_id=%s analysis_id=%s record_found=%s status=%s safe_error_code=%s lease_expired=not_applicable result_matches_current_identity=%s", request_id, record.get("id") if record else None, bool(record), record.get("status") if record else "none", record.get("safe_error_code") if record else None, bool(record))
        if record and record["status"] == "COMPLETED":
            logger.info("Replay Coach decision: request_id=%s analysis_id=%s action=REUSE_COMPLETED reason=IDENTITY_MATCH provider_will_be_called=False", request_id, record["id"])
            try:
                payload = record["analysis_json"]
                if isinstance(payload, str): payload = json.loads(payload)
                analysis = ReplayCoachAnalysis.model_validate(payload)
            except Exception as error:
                print(f"Replay Coach stored analysis invalid: analysis_id={record['id']} evidence_hash_prefix={prefix} error_type={type(error).__name__}")
                raise ReplayCoachResponseError() from error
            print(f"Replay Coach stored analysis reused: trade_date={identity['trade_date']} symbol={identity['normalized_symbol']} analysis_id={record['id']} evidence_hash_prefix={prefix} provider_called=False")
            return cls._result(context, analysis, record.get("provider_response_id"), {"model": record.get("actual_model")}, "stored", record, lifecycle=lifecycle)
        if not claimed:
            logger.warning("Replay Coach decision: request_id=%s analysis_id=%s action=SUPPRESS_CONCURRENT reason=PROCESSING_NOT_STALE provider_will_be_called=False", request_id, record.get("id") if record else None)
            print(f"Replay Coach concurrent request suppressed: trade_date={identity['trade_date']} symbol={identity['normalized_symbol']} evidence_hash_prefix={prefix}")
            raise ReplayCoachInProgressError()
        logger.info("Replay Coach decision: request_id=%s analysis_id=%s action=%s reason=%s provider_will_be_called=True", request_id, record["id"], "CLAIM_NEW" if record["status"] == "PROCESSING" else "RECLAIM_FAILED", "CLAIM_WON")
        # claim() commits before this point. Release the request connection before
        # the potentially minute-long provider call; completion/failure use new sessions.
        close = getattr(db, "close", None)
        if close:
            close()
        try:
            result = cls._generate(context, request_id=request_id, analysis_id=record["id"], lifecycle=lifecycle)
            if lifecycle is not None: lifecycle.active_operation = "COMPLETION_PERSISTENCE"
            cls._persist(repository, session_factory, "complete", record["id"], result.pop("_persisted_analysis"), result["openai_response_id"], result.pop("_usage"))
            print(f"Replay Coach record completed: analysis_id={record['id']} evidence_hash_prefix={prefix}")
            result.update({"result_source": "generated", "reused": False, "analysis_id": record["id"], "model": result.get("model")})
            return result
        except Exception as error:
            try:
                cls._persist(repository, session_factory, "fail", record["id"], getattr(error, "code", "REPLAY_COACH_FAILED"))
                print(f"Replay Coach record failed: analysis_id={record['id']} evidence_hash_prefix={prefix} reason={getattr(error, 'code', 'REPLAY_COACH_FAILED')}")
            except Exception as persistence_error:
                cls._log_persistence_failure(persistence_error, record["id"], "fail", True)
            raise

    @staticmethod
    def _persist(repository, session_factory, operation: str, analysis_id: int, *args) -> None:
        """Always persist final state using a newly checked-out short transaction."""
        db = session_factory()
        rollback_succeeded = False
        try:
            getattr(repository, operation)(db, analysis_id, *args)
        except Exception as error:
            try:
                db.rollback(); rollback_succeeded = True
            except Exception:
                pass
            ReplayCoachService._log_persistence_failure(error, analysis_id, operation, rollback_succeeded)
            raise
        finally:
            db.close()

    @staticmethod
    def _log_persistence_failure(error: Exception, analysis_id: int, operation: str, rollback_succeeded: bool) -> None:
        original = getattr(error, "orig", error)
        code = getattr(original, "args", [None])[0] if getattr(original, "args", None) else getattr(original, "code", None)
        message = " ".join(str(original).split())[:240]
        print("Replay Coach persistence failure: "
              f"exception_class={type(error).__name__} database_error_code={code!r} "
              f"database_message={message!r} operation={operation} analysis_id={analysis_id} "
              f"transaction_state=rolled_back rollback_succeeded={rollback_succeeded} fresh_session=True")

    @classmethod
    def _generate(cls, context: Dict[str, Any], request_id: str = "none", analysis_id=None, lifecycle=None) -> Dict[str, Any]:
        analysis, response_id, _usage = ReplayCoachOpenAIService.analyze(context, request_id=request_id, analysis_id=analysis_id, lifecycle=lifecycle)
        return cls._result(context, analysis, response_id, _usage, "generated", lifecycle=lifecycle) | {
            "_usage": _usage,
            "_persisted_analysis": analysis.model_dump(mode="json", exclude_computed_fields=True),
        }

    @classmethod
    def _result(cls, context: Dict[str, Any], analysis: ReplayCoachAnalysis, response_id: str, usage: Dict[str, Any], source: str, record=None, lifecycle=None) -> Dict[str, Any]:
        session_id = ReplayCoachSessionStore.create(context["trade_date"], context["stock"]["symbol"], response_id or "stored")
        try:
            if lifecycle is not None: lifecycle.active_operation = "API_SERIALIZATION"
            serialized_analysis = ReplayCoachResponsePresenter.present(analysis)
        except Exception as error:
            print(f"Replay Coach response diagnostic: reason=RESPONSE_SERIALIZATION_FAILED error_type={type(error).__name__}")
            raise ReplayCoachResponseError() from error
        if lifecycle is not None: lifecycle.active_operation = "COACH_SCORING"
        # score() is called inside the presenter; keeping this explicit stage
        # identifies a scoring failure before display construction.
        from backend.services.replay_coach_scoring_service import ReplayCoachScoringService
        decision_quality = ReplayCoachScoringService.score(context)
        if lifecycle is not None: lifecycle.active_operation = "COACH_PRESENTATION"
        coach_display = ReplayCoachResponsePresenter.coach_display(analysis, context, decision_quality)
        try:
            option_statuses = cls._decision_option_statuses(coach_display["decision_options"])
        except (KeyError, TypeError, ValueError) as error:
            print(f"Replay Coach response diagnostic: reason=PRESENTATION_OPTION_CONTRACT_INVALID error_type={type(error).__name__}")
            raise ReplayCoachResponseError() from error
        result = {"coach_session_id": session_id, "openai_response_id": response_id, "analysis": serialized_analysis, "coach_display": coach_display, "model": usage.get("model") or ReplayCoachOpenAIService.requested_model()}
        logging.getLogger(__name__).info(
            "Replay Coach presentation built: request_id=unavailable analysis_id=%s result_source=%s decision_score=%s best_decision=%s take_status=%s wait_status=%s no_trade_status=%s score_version=%s presentation_version=%s duration_ms=%s",
            record.get("id") if record else "none", source,
            coach_display["decision_quality_score"]["overall_score"],
            coach_display["my_best_trade_plan"]["decision"],
            option_statuses["TAKE"], option_statuses["WAIT"], option_statuses["NO_TRADE"],
            coach_display["decision_quality_score"]["score_version"],
            coach_display["presentation_version"],
            usage.get("duration_ms", "unavailable"),
        )
        if record is not None:
            result.update({"result_source": source, "reused": source == "stored", "analysis_id": record["id"], "generated_at": str(record.get("completed_at")), "model": usage.get("model") or record.get("requested_model") or ReplayCoachOpenAIService.requested_model()})
        return result

    @staticmethod
    def _decision_option_statuses(decision_options: list[dict[str, Any]]) -> dict[str, str]:
        """Validate the serialized presentation contract without relying on option order."""
        statuses = {option["decision"]: option["status"] for option in decision_options}
        required = {"TAKE", "WAIT", "NO_TRADE"}
        missing = required.difference(statuses)
        if missing:
            raise ValueError(f"missing decision option(s): {', '.join(sorted(missing))}")
        return {decision: statuses[decision] for decision in required}

    @classmethod
    def _stale_processing_seconds(cls) -> float:
        try: return max(float(os.getenv("OPENAI_REPLAY_COACH_STALE_PROCESSING_SECONDS", "180")), 180.0)
        except ValueError: return cls.STALE_PROCESSING_SECONDS


class ReplayCoachInProgressError(ReplayCoachError):
    code, status_code, public_message = "REPLAY_COACH_IN_PROGRESS", 409, "Replay Coach analysis is already in progress."
