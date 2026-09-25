"""Isolated OpenAI client for the Replay Coach request path."""
import json
import os
import logging
from time import perf_counter
from typing import Any, Dict

import httpx
from pydantic import ValidationError

from backend.models.replay_coach_model import ReplayCoachAnalysis
from backend.models.replay_coach_provider_model import ProviderReplayCoachTransport
from backend.services.replay_coach_adapter import to_application_analysis
from backend.services.replay_coach_config import load_replay_coach_environment, replay_coach_max_output_tokens


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


class ReplayCoachRateLimitError(ReplayCoachError):
    code, status_code, public_message = "OPENAI_RATE_LIMITED", 429, "Replay Coach is temporarily unavailable. Please try again later."


class ReplayCoachAuthenticationError(ReplayCoachError):
    code, status_code, public_message = "OPENAI_AUTH_FAILED", 503, "Replay Coach provider authentication failed."


class ReplayCoachResponseError(ReplayCoachError):
    code, status_code, public_message = "INVALID_COACH_RESPONSE", 502, "Replay Coach returned an invalid analysis."


class ReplayCoachOpenAIService:
    DEFAULT_MODEL = "gpt-5-mini"
    DEFAULT_TIMEOUT_SECONDS = 120.0
    SCHEMA_NAME = "replay_coach_analysis"
    PROMPT_VERSION = "replay_coach_prompt_v7"
    COACH_SCHEMA_VERSION = "replay_coach_schema_v5"

    @classmethod
    def requested_model(cls) -> str:
        return os.getenv("OPENAI_REPLAY_COACH_MODEL", cls.DEFAULT_MODEL)
    SYSTEM_INSTRUCTIONS = """You are an intraday trading coach helping a beginner understand a completed trade. Explain observations in simple language using exact supplied evidence. For each observation state the number, its supplied baseline, what the comparison means, whether it supports TAKE, WAIT, or NO TRADE, and the completed-candle time or price to inspect on the chart. Keep each explanation to one or two short sentences.

Do not calculate or provide ratings, component scores, overall scores, progress assessments, final classifications, or best-decision selection. The application owns all calculations, scoring, classifications, and final decisions. Legacy schema fields for risk, reward, and ratio are temporary compatibility fields: only echo supplied values and never treat them as your conclusion. Never invent evidence.

Analyze only supplied trade and candle evidence. Distinguish decision-time information from later outcomes. Important conclusions need timestamps and numeric evidence. Never invent indicators, VWAP, support, or resistance. NIFTY VWAP is unavailable unless supplied. Volume comparisons state their calculation. Alternatives are learning examples, not guarantees.

For an EXECUTED trade_data.plan_status, trade_data is the original documented plan linked to executed_trade; executed_trade is the actual execution and result, not a duplicate of the plan. decision_context contains deterministic no-lookahead facts: only its DECISION_TIME completed-candle facts may justify entry quality; post-entry evidence may describe outcome only. Use supplied documented_plan and decision_context values; do not calculate or invent financial, volume, VWAP, support, resistance, or scoring values. The minimum reward/risk ratio is 4.0 (reward divided by risk), so a TAKE is invalid below 4.0. If documented_plan.stop_present is true, the trade has a documented stop: never say the stop was missing or risk was undefined. You may critique stop distance, stop placement, low R:R, or target placement, but never a missing stop when stop_present is true. Do not infer broker-order placement or a missing documented stop from order_id=null, no executed_trade.stop_price, or execution_source=TRADE_JOURNAL.

Each issue appears once, with its evidence beneath it. Each how_to_improve item must prescribe an action rather than repeat criticism; do not repeat a missing-stop statement across sections. Return exactly the keyed trade, wait, and no_trade objects required by the schema. The key is authoritative: do not emit plan_type. TRADE requires direction and prices; WAIT and NO_TRADE must not include them. Give each plan concise non-empty reason, trigger_condition, invalidation_condition, and a supplied candle evidence_time or null. Return only schema-conforming JSON."""

    SYSTEM_INSTRUCTIONS += """

The application supplies authoritative coaching_facts and deterministic market metrics. Interpret only supplied facts; never calculate scores, statuses, risk/reward, thresholds, levels, touch counts, or best decisions. Every observation must name the supplied number, its baseline, what it means for the planned direction, and what to inspect on the chart. Do not use generic phrases such as 'configured threshold', 'mandatory rules', 'conditions become measurable', 'price invalidates the setup', 'structural stop required', or 'wait for confirmation'. State an exact supplied value, or say 'Not established from the available pre-entry evidence.' Do not invent prices, levels, times, thresholds, or indicators. Do not use incomplete or after-entry candle values to justify the original entry. A profitable outcome does not prove the original decision was strong. Keep explanations to two short sentences and return no scores, ratings, or status badges."""

    @classmethod
    def request_kwargs(cls, model: str, input_text: str, max_output_tokens: int) -> Dict[str, Any]:
        """Construct the exact SDK kwargs; callers must never log `input`."""
        return {"model": model, "input": [{"role": "developer", "content": cls.SYSTEM_INSTRUCTIONS}, {"role": "user", "content": input_text}], "text": {"format": {"type": "json_schema", "name": cls.SCHEMA_NAME, "strict": True, "schema": cls._strict_schema()}}, "max_output_tokens": max_output_tokens}

    @classmethod
    def analyze(cls, context: Dict[str, Any], request_id: str = "none", analysis_id=None, lifecycle=None) -> tuple[ReplayCoachAnalysis, str, Dict[str, Any]]:
        # Read at request time so a missing key affects only this endpoint.
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = cls.requested_model()
        timeout_seconds = cls._timeout_seconds()
        max_output_tokens, max_output_source = replay_coach_max_output_tokens()
        diagnostics = cls._request_diagnostics(context, openai_model, timeout_seconds)
        if not openai_api_key:
            raise ReplayCoachConfigurationError()
        started_at = perf_counter()
        logger = logging.getLogger(__name__)
        input_text = json.dumps(context, default=str)
        logger.info("Replay Coach provider request configured: request_id=%s analysis_id=%s model=%s method=responses.create schema_name=%s max_output_tokens_source=%s requested_max_output_tokens=%s reasoning_effort=unset input_character_count=%s input_byte_count=%s timeout_seconds=%s stream=False structured_output=True", request_id, analysis_id if analysis_id is not None else "none", openai_model, cls.SCHEMA_NAME, max_output_source, max_output_tokens, len(input_text), len(input_text.encode("utf-8")), timeout_seconds)
        try:
            client = cls._client(openai_api_key, timeout_seconds)
            if lifecycle is not None: lifecycle.provider_call_attempted = True; lifecycle.active_operation = "PROVIDER_CALL"
            response = client.responses.create(**cls.request_kwargs(openai_model, input_text, max_output_tokens))
            duration_ms = round((perf_counter() - started_at) * 1000)
        except (TimeoutError, httpx.TimeoutException) as error:
            cls._log_timeout(diagnostics, started_at)
            raise ReplayCoachTimeoutError() from error
        except Exception as error:
            if "timeout" in type(error).__name__.lower():
                cls._log_timeout(diagnostics, started_at)
                raise ReplayCoachTimeoutError() from error
            cls._log_provider_exception(error, openai_model, started_at)
            if cls._is_rate_limit_error(error):
                raise ReplayCoachRateLimitError() from error
            if cls._is_authentication_error(error):
                raise ReplayCoachAuthenticationError() from error
            raise ReplayCoachProviderError() from error

        # Usage is available on a received provider response even when its output
        # is incomplete, refused, malformed, or fails our Pydantic contract.
        response_id = getattr(response, "id", None)
        if lifecycle is not None:
            lifecycle.provider_response_received = True; lifecycle.provider_response_id = response_id
        usage = cls._usage_summary(response, duration_ms, context)
        status = getattr(response, "status", None) or "unknown"
        output_text = getattr(response, "output_text", None)
        logger.info("Replay Coach provider response received: request_id=%s analysis_id=%s provider_call_attempted=True provider_response_received=True response_id_present=%s status=%s model=%s requested_max_output_tokens=%s response_max_output_tokens=%s usage_object_present=%s input_tokens=%s output_tokens=%s total_tokens=%s cached_input_tokens=%s reasoning_tokens=%s output_text_present=%s output_text_length=%s output_item_count=%s incomplete_reason=%s provider_error_present=%s refusal_present=%s duration_ms=%s", request_id, analysis_id if analysis_id is not None else "none", bool(response_id), status, usage["model"], max_output_tokens, getattr(response, "max_output_tokens", None) if getattr(response, "max_output_tokens", None) is not None else "unavailable", getattr(response, "usage", None) is not None, *[usage[k] if usage[k] is not None else "unavailable" for k in ("input_tokens", "output_tokens", "total_tokens", "cached_input_tokens", "reasoning_tokens")], bool(output_text), len(output_text) if isinstance(output_text, str) else 0, len(getattr(response, "output", None) or []), cls._incomplete_reason(response) if status == "incomplete" else "none", bool(getattr(response, "error", None)), cls._has_refusal(response), duration_ms)

        if status != "completed":
            output_items = getattr(response, "output", None) or []
            types = [type(item).__name__ for item in output_items]
            visible = usage["output_tokens"] - usage["reasoning_tokens"] if isinstance(usage["output_tokens"], int) and isinstance(usage["reasoning_tokens"], int) else "unavailable"
            diagnostic = "USAGE_UNAVAILABLE" if getattr(response, "usage", None) is None else "MODEL_OR_CONTEXT_LIMIT_POSSIBLE"
            logger.warning("Replay Coach provider response incomplete: request_id=%s analysis_id=%s response_id=%s incomplete_reason=%s requested_max_output_tokens=%s response_max_output_tokens=%s usage_object_present=%s input_tokens=%s output_tokens=%s reasoning_tokens=%s visible_output_tokens=%s output_text_length=%s output_item_count=%s output_item_types=%s provider_error_present=%s refusal_present=%s token_limit_diagnostic=%s", request_id, analysis_id if analysis_id is not None else "none", response_id, cls._incomplete_reason(response), max_output_tokens, getattr(response, "max_output_tokens", None) if getattr(response, "max_output_tokens", None) is not None else "unavailable", getattr(response, "usage", None) is not None, usage["input_tokens"] if usage["input_tokens"] is not None else "unavailable", usage["output_tokens"] if usage["output_tokens"] is not None else "unavailable", usage["reasoning_tokens"] if usage["reasoning_tokens"] is not None else "unavailable", visible, len(output_text) if isinstance(output_text, str) else 0, len(output_items), types, bool(getattr(response, "error", None)), cls._has_refusal(response), diagnostic)
            cls._log_response_diagnostic(
                "PROVIDER_RESPONSE_INCOMPLETE",
                response_id=response_id,
                status=status,
                incomplete_reason=cls._incomplete_reason(response),
            )
            raise ReplayCoachResponseError()

        if cls._has_refusal(response):
            cls._log_response_diagnostic("PROVIDER_REFUSAL", response_id=response_id, status=status)
            raise ReplayCoachResponseError()

        if not isinstance(output_text, str) or not output_text.strip():
            cls._log_response_diagnostic("EMPTY_PROVIDER_OUTPUT", response_id=response_id, status=status)
            raise ReplayCoachResponseError()

        try:
            if lifecycle is not None: lifecycle.active_operation = "PROVIDER_OUTPUT_EXTRACTION"
            decoded_output = json.loads(output_text)
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            cls._log_response_diagnostic("PROVIDER_JSON_INVALID", response_id=response_id, status=status)
            raise ReplayCoachResponseError() from error
        try:
            if lifecycle is not None: lifecycle.active_operation = "PROVIDER_MODEL_VALIDATION"
            provider_analysis = ProviderReplayCoachTransport.model_validate(decoded_output)
        except (ValidationError, ValueError) as error:
            cls._log_validation_error(response_id, status, error, decoded_output)
            raise ReplayCoachResponseError() from error
        try:
            if lifecycle is not None: lifecycle.active_operation = "PROVIDER_TO_APPLICATION_ADAPTER"
            analysis = to_application_analysis(provider_analysis, context)
        except (ValidationError, ValueError) as error:
            cls._log_validation_error(response_id, status, error, decoded_output)
            raise ReplayCoachResponseError() from error
        try:
            if lifecycle is not None: lifecycle.active_operation = "CANONICAL_ANALYSIS_VALIDATION"
            analysis = ReplayCoachAnalysis.model_validate(analysis)
        except (ValidationError, ValueError) as error:
            cls._log_validation_error(response_id, status, error, decoded_output)
            raise ReplayCoachResponseError() from error
        if not response_id:
            cls._log_response_diagnostic("PROVIDER_RESPONSE_INCOMPLETE", response_id=None, status=status, incomplete_reason="missing_response_id")
            raise ReplayCoachResponseError()
        cls._log_usage(context, response_id, usage)
        return analysis, response_id, usage

    @classmethod
    def _timeout_seconds(cls) -> float:
        value = os.getenv("OPENAI_REPLAY_COACH_TIMEOUT_SECONDS")
        if value is None or not value.strip():
            return cls.DEFAULT_TIMEOUT_SECONDS
        try:
            configured = float(value)
        except ValueError:
            return cls.DEFAULT_TIMEOUT_SECONDS
        return configured if configured > 0 else cls.DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def _request_diagnostics(cls, context: Dict[str, Any], model: str, timeout_seconds: float) -> Dict[str, Any]:
        evidence_bytes = len(json.dumps(context, default=str, separators=(",", ":")).encode("utf-8"))
        schema_bytes = len(json.dumps(cls._strict_schema(), separators=(",", ":")).encode("utf-8"))
        prompt_bytes = len(cls.SYSTEM_INSTRUCTIONS.encode("utf-8"))
        return {
            "trade_date": context.get("trade_date"),
            "symbol": context.get("stock", {}).get("symbol"),
            "model": model,
            "timeout_seconds": timeout_seconds,
            "evidence_bytes": evidence_bytes,
            # This is intentionally an estimate only; the provider reports authoritative usage on success.
            "approx_input_tokens": round((evidence_bytes + schema_bytes + prompt_bytes) / 4),
        }

    @staticmethod
    def _log_timeout(diagnostics: Dict[str, Any], started_at: float) -> None:
        elapsed_ms = round((perf_counter() - started_at) * 1000)
        logging.getLogger(__name__).error("Replay Coach provider exception: reason=PROVIDER_TIMEOUT model=%s elapsed_ms=%s", diagnostics["model"], elapsed_ms)

    @classmethod
    def _log_provider_exception(cls, error: Exception, model: str, started_at: float) -> None:
        response = getattr(error, "response", None)
        headers = getattr(response, "headers", {}) or {}
        request_id = getattr(error, "request_id", None) or headers.get("x-request-id")
        status_code = getattr(error, "status_code", None) or getattr(response, "status_code", None)
        error_code = getattr(error, "code", None)
        error_type = getattr(error, "type", None)
        elapsed_ms = round((perf_counter() - started_at) * 1000)
        logging.getLogger(__name__).error("Replay Coach provider exception: reason=%s exception_class=%s http_status=%s provider_error_code=%s provider_error_type=%s provider_request_id=%s model=%s elapsed_ms=%s", cls._provider_exception_reason(error, status_code), type(error).__name__, status_code, error_code, error_type, request_id, model, elapsed_ms)

    @staticmethod
    def _sanitize_provider_message(error: Exception) -> str:
        message = " ".join(str(getattr(error, "message", None) or str(error)).split())
        # Provider errors can echo invalid schema fragments; retain a small, safe diagnostic only.
        return repr(message[:240])

    @classmethod
    def _provider_exception_reason(cls, error: Exception, status_code: Any) -> str:
        if cls._is_rate_limit_error(error):
            return "PROVIDER_RATE_LIMITED"
        if cls._is_authentication_error(error):
            return "PROVIDER_AUTHENTICATION_FAILED"
        if status_code == 400 or "badrequest" in type(error).__name__.lower():
            return "PROVIDER_BAD_REQUEST"
        return "PROVIDER_API_FAILED"

    @staticmethod
    def _incomplete_reason(response: Any) -> Any:
        details = getattr(response, "incomplete_details", None)
        reason = getattr(details, "reason", None)
        return reason if reason is not None else "unknown"

    @staticmethod
    def _has_refusal(response: Any) -> bool:
        if getattr(response, "refusal", None):
            return True
        for item in getattr(response, "output", None) or []:
            for content in getattr(item, "content", None) or []:
                if getattr(content, "refusal", None):
                    return True
        return False

    @staticmethod
    def _log_response_diagnostic(reason: str, **fields: Any) -> None:
        values = " ".join(f"{name}={value}" for name, value in fields.items())
        logging.getLogger(__name__).warning("Replay Coach validation failure: reason=%s %s", reason, values)

    @classmethod
    def _log_validation_error(cls, response_id: Any, status: str, error: ValidationError | ValueError, output: Any) -> None:
        if isinstance(error, ValidationError):
            sanitized_errors = [
                {"path": ".".join(str(part) for part in item["loc"]), "type": item["type"], "message": item["msg"]}
                for item in error.errors(include_url=False)
            ]
        else:
            sanitized_errors = [{"path": "adapter", "type": type(error).__name__, "message": str(error)}]
        cls._log_response_diagnostic(
            "COACH_SCHEMA_VALIDATION_FAILED",
            response_id=response_id,
            status=status,
            errors=sanitized_errors,
            **cls._plan_structure(output),
        )

    @staticmethod
    def _plan_structure(value: Any) -> Dict[str, Any]:
        plans = value.get("alternative_trade_plans") if isinstance(value, dict) else None
        return {"plan_keys": sorted(plans) if isinstance(plans, dict) else None, "plan_type": type(plans).__name__}

    @staticmethod
    def _usage_summary(response: Any, duration_ms: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Read optional OpenAI usage fields without making them part of the API contract."""
        usage = getattr(response, "usage", None)
        input_details = getattr(usage, "input_tokens_details", None)
        output_details = getattr(usage, "output_tokens_details", None)
        return {
            "model": getattr(response, "model", None),
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
            "cached_input_tokens": getattr(input_details, "cached_tokens", None),
            "reasoning_tokens": getattr(output_details, "reasoning_tokens", None),
            "duration_ms": duration_ms,
            "evidence_bytes": len(json.dumps(context, default=str, separators=(",", ":")).encode("utf-8")),
        }

    @staticmethod
    def _log_usage(context: Dict[str, Any], response_id: str, usage: Dict[str, Any]) -> None:
        logging.getLogger(__name__).info("Replay Coach request completed: response_id=%s model=%s input_tokens=%s output_tokens=%s total_tokens=%s reasoning_tokens=%s duration_ms=%s", response_id, usage["model"], usage["input_tokens"], usage["output_tokens"], usage["total_tokens"], usage["reasoning_tokens"], usage["duration_ms"])

    @staticmethod
    def _is_rate_limit_error(error: Exception) -> bool:
        return getattr(error, "status_code", None) == 429 or "ratelimit" in type(error).__name__.lower() or "rate_limit" in type(error).__name__.lower()

    @staticmethod
    def _is_authentication_error(error: Exception) -> bool:
        return getattr(error, "status_code", None) in (401, 403) or "authentication" in type(error).__name__.lower()

    @classmethod
    def _client(cls, openai_api_key: str, timeout_seconds: float):
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ReplayCoachConfigurationError() from error
        # max_retries=0 is required: a timeout can leave the provider processing
        # the original request, so an SDK retry could create another paid request.
        return OpenAI(api_key=openai_api_key, timeout=timeout_seconds, max_retries=0)

    @staticmethod
    def _strict_schema():
        # The provider must not supply derived arithmetic.  The application
        # contract adds risk/reward/R:R only after deterministic calculation.
        schema = ProviderReplayCoachTransport.model_json_schema()

        def visit(value):
            if isinstance(value, dict):
                # Pydantic represents a discriminated union as oneOf plus a
                # discriminator. OpenAI Structured Outputs permits nested anyOf,
                # not oneOf/discriminator. The plan_type const in each closed
                # variant still keeps the three contracts mutually exclusive.
                if "oneOf" in value:
                    value["anyOf"] = value.pop("oneOf")
                value.pop("discriminator", None)
                # Strict Structured Outputs requires nullable values to remain
                # required; defaults are neither needed nor part of the subset.
                value.pop("default", None)
                if isinstance(value.get("properties"), dict):
                    value["required"] = list(value["properties"])
                for child in value.values(): visit(child)
            elif isinstance(value, list):
                for child in value: visit(child)

        visit(schema)
        # Keep the provider-facing branch self-contained: OpenAI receives one
        # fixed object, not references, unions, or an array it could duplicate.
        scalar = lambda kind: {"type": kind}
        nullable_time = {"anyOf": [scalar("string"), scalar("null")]}
        common = {
            "rating": {"type": "integer", "minimum": 1, "maximum": 10},
            "reason": {"type": "string", "minLength": 1},
            "trigger_condition": {"type": "string", "minLength": 1},
            "invalidation_condition": {"type": "string", "minLength": 1},
            "evidence_time": nullable_time,
        }
        def closed(properties):
            return {"type": "object", "additionalProperties": False, "properties": properties, "required": list(properties)}
        trade = closed({"direction": {"type": "string", "enum": ["LONG", "SHORT"]}, "entry": scalar("number"), "stop": scalar("number"), "target": scalar("number"), **common})
        wait = closed(dict(common))
        schema["properties"]["alternative_trade_plans"] = closed({"trade": trade, "wait": wait, "no_trade": closed(dict(common))})
        return schema
