"""Dedicated, grounded provider operation for Coach follow-up answers."""
import json, logging, os
from time import perf_counter
import httpx
from pydantic import ValidationError
from backend.models.replay_coach_follow_up_model import FollowUpProviderAnswer
from backend.services.replay_coach_openai_service import (ReplayCoachConfigurationError, ReplayCoachTimeoutError, ReplayCoachProviderError, ReplayCoachRateLimitError, ReplayCoachAuthenticationError, ReplayCoachResponseError, ReplayCoachOpenAIService)
from backend.services.replay_coach_config import replay_coach_max_output_tokens

FOLLOW_UP_PROMPT_VERSION="replay_coach_follow_up_v2"
FOLLOW_UP_SCHEMA_VERSION="replay_coach_follow_up_schema_v1"
FOLLOW_UP_COACH_INSTRUCTIONS="""You explain an already completed Replay Coach analysis. Answer the current question first in beginner-friendly Markdown. Infer whether it concerns the executed trade, full-session plan, or both; compare them when that improves learning. Ask one concise clarification question only when a reference is genuinely ambiguous. Distinguish executed-trade values from suggested-plan values and decision-time evidence from hindsight. Explain NIFTY behavior, stock behavior, their relationship, and trading implication when relevant. Do not regenerate or alter either stored analysis or expose hidden reasoning.

Evidence priority: (1) stored market evidence is authoritative for prices, candles, times, VWAP, volume, NIFTY behavior, trade facts and calculations; (2) stored Coach analyses are authoritative for their original evaluation and plan; (3) previous completed conversation only resolves references and continuity; (4) user questions are not verified market facts; (5) verify prior assistant claims against stored evidence; (6) explain conflicts using stored evidence; (7) state exactly what is unavailable rather than inventing any value, time, candle, calculation, level, or market event. Return only the strict JSON schema."""

class ReplayCoachFollowUpOpenAIService:
    @classmethod
    def analyze(cls, context, request_id="none", analysis_id=None):
        key=os.getenv("OPENAI_API_KEY")
        if not key: raise ReplayCoachConfigurationError()
        model=ReplayCoachOpenAIService.requested_model(); timeout=ReplayCoachOpenAIService._timeout_seconds(); maximum,_=replay_coach_max_output_tokens(); started=perf_counter()
        try:
            response=ReplayCoachOpenAIService._client(key,timeout).responses.create(model=model,input=[{"role":"developer","content":FOLLOW_UP_COACH_INSTRUCTIONS},{"role":"user","content":json.dumps(context,default=str)}],text={"format":{"type":"json_schema","name":"replay_coach_follow_up","strict":True,"schema":cls._schema()}},max_output_tokens=maximum)
        except (TimeoutError,httpx.TimeoutException) as error:
            ReplayCoachOpenAIService._log_timeout({"model":model},started)
            raise ReplayCoachTimeoutError() from error
        except Exception as error:
            if "timeout" in type(error).__name__.lower():
                ReplayCoachOpenAIService._log_timeout({"model":model},started)
                raise ReplayCoachTimeoutError() from error
            ReplayCoachOpenAIService._log_provider_exception(error,model,started)
            if ReplayCoachOpenAIService._is_rate_limit_error(error): raise ReplayCoachRateLimitError() from error
            if ReplayCoachOpenAIService._is_authentication_error(error): raise ReplayCoachAuthenticationError() from error
            raise ReplayCoachProviderError() from error
        response_id=getattr(response,"id",None); output=getattr(response,"output_text",None)
        if getattr(response,"status",None)!="completed" or ReplayCoachOpenAIService._has_refusal(response) or not isinstance(output,str) or not output.strip() or not response_id: raise ReplayCoachResponseError()
        try: answer=FollowUpProviderAnswer.model_validate(json.loads(output))
        except (ValueError,ValidationError,json.JSONDecodeError) as error: raise ReplayCoachResponseError() from error
        usage=ReplayCoachOpenAIService._usage_summary(response,round((perf_counter()-started)*1000),context)
        logging.getLogger(__name__).info("Replay Coach follow-up provider completed: request_id=%s analysis_id=%s model=%s prompt_version=%s tokens=%s duration_ms=%s",request_id,analysis_id,usage.get("model"),FOLLOW_UP_PROMPT_VERSION,usage.get("total_tokens"),usage.get("duration_ms"))
        return answer,response_id,usage
    @staticmethod
    def _schema():
        schema=FollowUpProviderAnswer.model_json_schema()
        def visit(v):
            if isinstance(v,dict):
                v.pop("default",None)
                if isinstance(v.get("properties"),dict): v["required"]=list(v["properties"])
                for x in v.values(): visit(x)
            elif isinstance(v,list):
                for x in v: visit(x)
        visit(schema); return schema
