"""Short-transaction persistence for Replay Coach idempotency."""
from datetime import datetime, timedelta
import json
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
    def claim(cls, db: Session, identity: Dict[str, Any], stale_after_seconds: float):
        """Return (record, won). Commits before the provider call."""
        values = {**identity, "status": "PROCESSING", "coach_session_id": str(uuid4()), "symbol": identity["normalized_symbol"],
                  "evidence_json": identity["evidence_json"], "schema_version": identity["coach_schema_version"], "model": identity["requested_model"]}
        try:
            db.execute(text("""INSERT INTO replay_coach_analysis
                (coach_session_id, trade_id, trade_date, symbol, normalized_symbol, context_version, evidence_hash, evidence_json,
                 prompt_version, schema_version, coach_schema_version, model, requested_model, status)
                VALUES (:coach_session_id,:trade_id,:trade_date,:symbol,:normalized_symbol,:context_version,:evidence_hash,CAST(:evidence_json AS JSON),
                 :prompt_version,:schema_version,:coach_schema_version,:model,:requested_model,:status)"""), values)
            db.commit()
            return cls.find(db, identity), True
        except IntegrityError:
            db.rollback()
        record = cls.find(db, identity)
        if not record:
            return None, False
        if record["status"] == "FAILED":
            result = db.execute(text("""UPDATE replay_coach_analysis SET status='PROCESSING', failure_reason=NULL, updated_at=CURRENT_TIMESTAMP
                WHERE id=:id AND status='FAILED'"""), {"id": record["id"]})
            db.commit()
            return cls.find(db, identity), result.rowcount == 1
        if record["status"] == "PROCESSING":
            threshold = datetime.utcnow() - timedelta(seconds=stale_after_seconds)
            result = db.execute(text("""UPDATE replay_coach_analysis SET updated_at=CURRENT_TIMESTAMP
                WHERE id=:id AND status='PROCESSING' AND updated_at < :threshold"""), {"id": record["id"], "threshold": threshold})
            db.commit()
            return cls.find(db, identity), result.rowcount == 1
        return record, False

    @staticmethod
    def complete(db: Session, analysis_id: int, analysis: Dict[str, Any], response_id: str, usage: Dict[str, Any]):
        db.execute(text("""UPDATE replay_coach_analysis SET status='COMPLETED', actual_model=:actual_model,
            openai_response_id=:provider_response_id, analysis_json=CAST(:analysis_json AS JSON),
            input_tokens=:input_tokens, output_tokens=:output_tokens, total_tokens=:total_tokens,
            cached_tokens=:cached_input_tokens, reasoning_tokens=:reasoning_tokens,
            duration_ms=:duration_ms, evidence_bytes=:evidence_bytes, completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
            WHERE id=:id AND status='PROCESSING'"""), {"id": analysis_id, "actual_model": usage.get("model"), "provider_response_id": response_id,
            "analysis_json": json.dumps(analysis, separators=(",", ":")), **usage})
        db.commit()

    @staticmethod
    def fail(db: Session, analysis_id: int, reason: str):
        db.execute(text("""UPDATE replay_coach_analysis SET status='FAILED', failure_reason=:reason, updated_at=CURRENT_TIMESTAMP
            WHERE id=:id AND status='PROCESSING'"""), {"id": analysis_id, "reason": reason[:64]})
        db.commit()
