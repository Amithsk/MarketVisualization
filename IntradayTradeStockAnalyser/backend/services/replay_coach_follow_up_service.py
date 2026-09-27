"""Orchestrates persisted, evidence-grounded follow-up questions."""
import json
import logging
from datetime import datetime, timezone
from backend.repositories.replay_coach_message_repository import ReplayCoachMessageRepository
from backend.services.replay_coach_follow_up_openai_service import ReplayCoachFollowUpOpenAIService, FOLLOW_UP_PROMPT_VERSION, FOLLOW_UP_SCHEMA_VERSION
from backend.services.replay_coach_openai_service import ReplayCoachError

class ReplayCoachFollowUpService:
    logger = logging.getLogger(__name__)
    @staticmethod
    def _times(evidence):
        found=set()
        def scan(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    if key in {"time","timestamp"} and isinstance(item,str): found.add(item)
                    scan(item)
            elif isinstance(value,list):
                for item in value: scan(item)
        scan(evidence); return found
    @staticmethod
    def _time_key(value):
        if not isinstance(value, str): return None
        try:
            parsed=datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
            if parsed.tzinfo: parsed=parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed.isoformat(timespec="seconds")
        except ValueError:
            return value.strip()
    @classmethod
    def _normalize_evidence_times(cls, requested, evidence):
        stored=cls._times(evidence)
        canonical={cls._time_key(value): value for value in stored}
        clock={}
        for value in stored:
            try: clock.setdefault(datetime.fromisoformat(value.strip().replace("Z", "+00:00")).strftime("%H:%M"),[]).append(value)
            except (TypeError, ValueError): pass
        normalized=[]; discarded=0
        for value in requested:
            match=canonical.get(cls._time_key(value))
            if not match and isinstance(value,str):
                candidates=clock.get(value.strip(),[])
                match=candidates[0] if len(candidates)==1 else None
            if not match:
                discarded+=1
                continue
            if match not in normalized: normalized.append(match)
        return normalized, discarded
    @classmethod
    def _context(cls,snapshot,history,current_user):
        analysis=snapshot["analysis_json"]; evidence=snapshot["evidence_json"]
        earlier=[row for row in history if row["sequence_number"] < current_user["sequence_number"]]
        assistants={row["reply_to_message_id"]:row for row in earlier if row["role"]=="ASSISTANT" and row["status"]=="COMPLETED" and row["analysis_id"]==current_user["analysis_id"]}
        previous=[]
        for row in earlier:
            reply=assistants.get(row["id"])
            if row["role"]=="USER" and row["status"]=="COMPLETED" and reply and reply["analysis_id"]==row["analysis_id"]:
                previous.extend([{"role":"USER","content":row["content"]},{"role":"ASSISTANT","content":reply["content"]}])
        return {"SECTION 1 — AUTHORITATIVE STORED ANALYSIS":{"executed_trade_analysis":analysis.get("executed_trade_analysis"),"best_full_session_plan":analysis.get("best_full_session_plan"),"key_learning":analysis.get("key_learning"),"limitations":analysis.get("limitations")},"SECTION 2 — AUTHORITATIVE STORED MARKET EVIDENCE":{"evidence_json":evidence,"evidence_hash":snapshot["evidence_hash"],"context_version":snapshot.get("context_version")},"SECTION 3 — PREVIOUS COMPLETED CONVERSATION":previous,"SECTION 4 — CURRENT QUESTION":current_user["content"]}
    @staticmethod
    def present(row):
        times=row.get("evidence_times_json") or []
        if isinstance(times,str): times=json.loads(times)
        feedback=None
        if row.get("feedback_id"):
            feedback={"id":row["feedback_id"],"rating":row["feedback_rating"],"reason_code":row["feedback_reason_code"],"comment":row["feedback_comment"]}
        return {"id":row["id"],"analysis_id":row["analysis_id"],"sequence_number":row["sequence_number"],"role":row["role"],"content":row["content"],"status":row["status"],"reply_to_message_id":row["reply_to_message_id"],"inferred_intent":row["inferred_intent"],"evidence_times":times,"safe_error_code":row["safe_error_code"],"created_at":str(row["created_at"]),"completed_at":str(row["completed_at"]) if row.get("completed_at") else None,"feedback":feedback}
    @classmethod
    def ask(cls,db,analysis_id,request,request_id="none"):
        user,claim=ReplayCoachMessageRepository.claim_user_message(db,analysis_id,request.question,request.client_request_id)
        if not user: return {"state":"ANALYSIS_UNAVAILABLE"}
        if claim != "CREATED":
            reply=ReplayCoachMessageRepository.get_assistant_reply(db,user["id"])
            return {"state":claim,"user_message":cls.present(user),"assistant_message":cls.present(reply) if reply else None}
        stage="LOAD_SNAPSHOT"; response_id=None; provider_evidence_count=0; stored_evidence_count=0
        try:
            snapshot=ReplayCoachMessageRepository.load_completed_analysis_snapshot(db,analysis_id)
            if not snapshot: raise ValueError("completed snapshot unavailable")
            stage="LOAD_HISTORY"
            history=ReplayCoachMessageRepository.list_messages_by_analysis_id(db,analysis_id)
            stage="BUILD_CONTEXT"
            context=cls._context(snapshot,history,user)
            stage="PROVIDER_CALL"
            answer,response_id,usage=ReplayCoachFollowUpOpenAIService.analyze(context,request_id,analysis_id)
            provider_evidence_count=len(answer.evidence_times)
            stored_evidence_count=len(cls._times(snapshot["evidence_json"]))
            stage="VALIDATE_EVIDENCE_TIMES"
            normalized_times,discarded_evidence_count=cls._normalize_evidence_times(answer.evidence_times,snapshot["evidence_json"])
            if discarded_evidence_count:
                cls.logger.warning("Replay Coach follow-up evidence annotations discarded: request_id=%s analysis_id=%s user_message_id=%s discarded_reference_count=%s accepted_reference_count=%s",request_id,analysis_id,user["id"],discarded_evidence_count,len(normalized_times))
            stage="PERSIST_ASSISTANT_REPLY"
            assistant=ReplayCoachMessageRepository.complete_with_assistant_message(db,analysis_id,user["id"],answer.answer,answer.inferred_intent.value,normalized_times,response_id,usage.get("model"),FOLLOW_UP_PROMPT_VERSION,usage)
            cls.logger.info("Replay Coach follow-up completed: request_id=%s analysis_id=%s user_message_id=%s assistant_message_id=%s operation=%s provider_response_id_present=%s inferred_intent=%s evidence_reference_count=%s stored_evidence_time_count=%s model=%s prompt_version=%s schema_version=%s total_tokens=%s",request_id,analysis_id,user["id"],assistant["id"],stage,bool(response_id),answer.inferred_intent.value,provider_evidence_count,stored_evidence_count,usage.get("model"),FOLLOW_UP_PROMPT_VERSION,FOLLOW_UP_SCHEMA_VERSION,usage.get("total_tokens"))
            return {"state":"COMPLETED","user_message":cls.present(user),"assistant_message":cls.present(assistant)}
        except ReplayCoachError as error:
            ReplayCoachMessageRepository.fail_user_message(db,user["id"],error.code); return {"state":"FAILED","new_attempt":True,"user_message":cls.present(ReplayCoachMessageRepository.find_by_client_request_id(db,analysis_id,request.client_request_id)),"safe_error_code":error.code}
        except Exception as error:
            reason="UNKNOWN_EVIDENCE_TIMESTAMP" if isinstance(error,ValueError) and str(error)=="unknown evidence timestamp" else "UNEXPECTED_APPLICATION_FAILURE"
            cls.logger.warning("Replay Coach follow-up failed: request_id=%s analysis_id=%s user_message_id=%s operation=%s failure_reason=%s exception_class=%s provider_response_id_present=%s evidence_reference_count=%s stored_evidence_time_count=%s",request_id,analysis_id,user["id"],stage,reason,type(error).__name__,bool(response_id),provider_evidence_count,stored_evidence_count)
            ReplayCoachMessageRepository.fail_user_message(db,user["id"],"INVALID_FOLLOW_UP_RESPONSE"); return {"state":"FAILED","new_attempt":True,"user_message":cls.present(ReplayCoachMessageRepository.find_by_client_request_id(db,analysis_id,request.client_request_id)),"safe_error_code":"INVALID_FOLLOW_UP_RESPONSE"}
