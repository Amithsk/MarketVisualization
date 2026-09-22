"""Short-transaction persistence for Replay Coach idempotency."""
from datetime import datetime, timedelta
import json
import logging
import re
from time import perf_counter
from uuid import uuid4
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class ReplayCoachRepository:
    IDENTITY = ("trade_date", "normalized_symbol", "context_version", "evidence_hash", "prompt_version", "coach_schema_version", "requested_model")

    @staticmethod
    def find(db: Session, identity: Dict[str, Any]):
        where = " AND ".join(f"{field}=:{field}" for field in ReplayCoachRepository.IDENTITY)
        return db.execute(text(f"SELECT * FROM replay_coach_analysis WHERE {where} LIMIT 1"), identity).mappings().first()

    @classmethod
    def claim(cls, db: Session, identity: Dict[str, Any], stale_after_seconds: float, request_id: str = "none"):
        """Return (record, won). Commits before the provider call."""
        logger, started, analysis_id, operation = logging.getLogger(__name__), perf_counter(), None, "CLAIM_INSERT"
        logger.info("Replay Coach claim started: request_id=%s trade_date=%s symbol=%s evidence_hash_prefix=%s requested_model=%s", request_id, identity["trade_date"], identity["normalized_symbol"], identity["evidence_hash"][:12], identity["requested_model"])
        values = {**identity, "status": "PROCESSING", "coach_session_id": str(uuid4()), "symbol": identity["normalized_symbol"],
                  "evidence_json": identity["evidence_json"], "schema_version": identity["coach_schema_version"], "model": identity["requested_model"]}
        try:
            db.execute(text("""INSERT INTO replay_coach_analysis
                (coach_session_id, trade_id, trade_date, symbol, normalized_symbol, context_version, evidence_hash, evidence_json,
                 prompt_version, schema_version, coach_schema_version, model, requested_model, status)
                VALUES (:coach_session_id,:trade_id,:trade_date,:symbol,:normalized_symbol,:context_version,:evidence_hash,CAST(:evidence_json AS JSON),
                 :prompt_version,:schema_version,:coach_schema_version,:model,:requested_model,:status)"""), values)
            db.commit()
            operation = "CLAIM_LOOKUP"; record = cls.find(db, identity); analysis_id = record["id"] if record else None
            logger.info("Replay Coach claim completed: request_id=%s operation=CLAIM_INSERT analysis_id=%s status=PROCESSING claimed=True elapsed_ms=%s", request_id, analysis_id, round((perf_counter()-started)*1000))
            return record, True
        except IntegrityError:
            rollback_ok = cls._rollback(db)
            logger.warning("Replay Coach claim duplicate detected: request_id=%s operation=CLAIM_INSERT integrity_error_type=duplicate_identity rollback_attempted=True rollback_succeeded=%s elapsed_ms=%s", request_id, rollback_ok, round((perf_counter()-started)*1000))
        except Exception as error:
            cls._log_db_error(logger, request_id, operation, analysis_id, error, db, started); raise
        try:
            operation = "CLAIM_LOOKUP"; record = cls.find(db, identity); analysis_id = record["id"] if record else None
        except Exception as error:
            cls._log_db_error(logger, request_id, operation, analysis_id, error, db, started); raise
        if not record:
            return None, False
        logger.info("Replay Coach existing record found: request_id=%s operation=CLAIM_LOOKUP analysis_id=%s status=%s safe_error_code=%s lease_expired=not_applicable elapsed_ms=%s", request_id, analysis_id, record["status"], record.get("safe_error_code") or "none", round((perf_counter()-started)*1000))
        if record["status"] == "FAILED":
            operation = "RECLAIM_FAILED_UPDATE"; logger.info("Replay Coach failed reclaim started: request_id=%s operation=%s analysis_id=%s previous_status=FAILED", request_id, operation, analysis_id)
            try:
                result = db.execute(text("""UPDATE replay_coach_analysis SET status='PROCESSING', failure_reason=NULL, updated_at=CURRENT_TIMESTAMP
                    WHERE id=:id AND status='FAILED'"""), {"id": analysis_id})
                if not result.rowcount:
                    db.commit(); logger.warning("Replay Coach failed reclaim not acquired: request_id=%s operation=RECLAIM_FAILED_UPDATE analysis_id=%s rows_affected=0 reason=STATUS_CHANGED claimed=False elapsed_ms=%s", request_id, analysis_id, round((perf_counter()-started)*1000)); return cls.find(db, identity), False
                operation = "RECLAIM_FAILED_COMMIT"; db.commit()
                operation = "RECLAIM_FAILED_RELOAD"; refreshed = cls.find(db, identity)
                logger.info("Replay Coach failed reclaim completed: request_id=%s operation=RECLAIM_FAILED_COMMIT analysis_id=%s previous_status=FAILED new_status=PROCESSING rows_affected=%s claimed=True elapsed_ms=%s", request_id, analysis_id, result.rowcount, round((perf_counter()-started)*1000))
                return refreshed, True
            except Exception as error:
                cls._log_db_error(logger, request_id, operation, analysis_id, error, db, started); raise
        if record["status"] == "PROCESSING":
            threshold = datetime.utcnow() - timedelta(seconds=stale_after_seconds)
            result = db.execute(text("""UPDATE replay_coach_analysis SET updated_at=CURRENT_TIMESTAMP
                WHERE id=:id AND status='PROCESSING' AND updated_at < :threshold"""), {"id": record["id"], "threshold": threshold})
            db.commit()
            return cls.find(db, identity), result.rowcount == 1
        return record, False

    @staticmethod
    def _rollback(db: Session) -> bool:
        try: db.rollback(); return True
        except Exception: return False

    @classmethod
    def _log_db_error(cls, logger, request_id, operation, analysis_id, error, db, started):
        rollback_ok = cls._rollback(db)
        original = getattr(error, "orig", None); args = getattr(original, "args", ()) or ()
        code = args[0] if args and isinstance(args[0], int) else None
        message = args[1] if len(args) > 1 else str(original or error)
        # Strip URL/userinfo and cap output; no SQL/parameters are emitted by this helper.
        message = re.sub(r"\w+://\S+|\w+:\S+@\S+", "[redacted]", " ".join(str(message).split()))[:300]
        logger.error("Replay Coach database operation failed: request_id=%s operation=%s analysis_id=%s exception_class=%s dbapi_exception_class=%s database_error_code=%s database_message=%r rollback_attempted=True rollback_succeeded=%s elapsed_ms=%s", request_id, operation, analysis_id if analysis_id is not None else "none", type(error).__name__, type(original).__name__ if original else "none", code, message, rollback_ok, round((perf_counter()-started)*1000))

    @staticmethod
    def complete(db: Session, analysis_id: int, analysis: Dict[str, Any], response_id: str, usage: Dict[str, Any]):
        result = db.execute(text("""UPDATE replay_coach_analysis SET status='COMPLETED', actual_model=:actual_model,
            openai_response_id=:provider_response_id, analysis_json=CAST(:analysis_json AS JSON),
            input_tokens=:input_tokens, output_tokens=:output_tokens, total_tokens=:total_tokens,
            cached_tokens=:cached_input_tokens, reasoning_tokens=:reasoning_tokens,
            duration_ms=:duration_ms, evidence_bytes=:evidence_bytes, completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
            WHERE id=:id AND status='PROCESSING'"""), {"id": analysis_id, "actual_model": usage.get("model"), "provider_response_id": response_id,
            "analysis_json": json.dumps(analysis, separators=(",", ":")), **usage})
        db.commit()
        if result.rowcount != 1:
            raise RuntimeError("Replay Coach completion lost its PROCESSING claim.")

    @staticmethod
    def fail(db: Session, analysis_id: int, reason: str):
        result = db.execute(text("""UPDATE replay_coach_analysis SET status='FAILED', safe_error_code=:code,
            failure_reason=:reason, updated_at=CURRENT_TIMESTAMP
            WHERE id=:id AND status='PROCESSING'"""), {"id": analysis_id, "code": reason[:64], "reason": reason[:64]})
        db.commit()
        if result.rowcount != 1:
            raise RuntimeError("Replay Coach failure update lost its PROCESSING claim.")
