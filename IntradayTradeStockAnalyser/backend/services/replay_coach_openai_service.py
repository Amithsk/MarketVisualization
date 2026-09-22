"""Isolated OpenAI client for the Replay Coach request path."""
import json
import os
from time import perf_counter
from typing import Any, Dict

import httpx
from pydantic import ValidationError

from backend.models.replay_coach_model import ProviderReplayCoachAnalysis, ReplayCoachAnalysis, to_application_analysis
from backend.services.replay_coach_config import load_replay_coach_environment


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
    PROMPT_VERSION = "replay_coach_prompt_v1"
    COACH_SCHEMA_VERSION = "replay_coach_schema_v2"

    @classmethod
    def requested_model(cls) -> str:
        return os.getenv("OPENAI_REPLAY_COACH_MODEL", cls.DEFAULT_MODEL)
    SYSTEM_INSTRUCTIONS = """You are a rigorous intraday Trade Replay Coach. Analyze only the supplied executed trade and candle evidence. Use whole-session stock and NIFTY Futures candles, but distinguish information knowable at a decision time from later outcomes. Every important conclusion needs candle timestamps and numeric evidence. Never invent VWAP, indicators, support, or resistance. NIFTY VWAP is unavailable unless supplied. Volume comparisons must state their calculation. Alternative plans are retrospective learning examples, not guarantees. Return only JSON conforming to the supplied schema."""

    @classmethod
    def analyze(cls, context: Dict[str, Any]) -> tuple[ReplayCoachAnalysis, str, Dict[str, Any]]:
        # Read at request time so a missing key affects only this endpoint.
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = cls.requested_model()
        timeout_seconds = cls._timeout_seconds()
        diagnostics = cls._request_diagnostics(context, openai_model, timeout_seconds)
        print(f"OpenAI API key configured: {bool(openai_api_key)}")
        print(f"Replay Coach model: {openai_model}")
        if not openai_api_key:
            raise ReplayCoachConfigurationError()
        started_at = perf_counter()
        try:
            client = cls._client(openai_api_key, timeout_seconds)
            response = client.responses.create(
                model=openai_model,
                input=[
                    {"role": "developer", "content": cls.SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": json.dumps(context, default=str)},
                ],
                text={"format": {"type": "json_schema", "name": cls.SCHEMA_NAME, "strict": True, "schema": cls._strict_schema()}},
            )
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
        usage = cls._usage_summary(response, duration_ms, context)
        status = getattr(response, "status", None) or "unknown"
        output_text = getattr(response, "output_text", None)
        cls._log_response_received(response_id, status, output_text, usage)

        if status != "completed":
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
            decoded_output = json.loads(output_text)
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            cls._log_response_diagnostic("PROVIDER_JSON_INVALID", response_id=response_id, status=status)
            raise ReplayCoachResponseError() from error
        try:
            provider_analysis = ProviderReplayCoachAnalysis.model_validate(decoded_output)
            analysis = to_application_analysis(provider_analysis)
        except (ValidationError, ValueError) as error:
            cls._log_validation_error(response_id, status, error)
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
        print(
            "Replay Coach provider exception: reason=PROVIDER_TIMEOUT "
            f"trade_date={diagnostics['trade_date']} "
            f"symbol={diagnostics['symbol']} "
            f"model={diagnostics['model']} "
            f"configured_timeout_seconds={diagnostics['timeout_seconds']} "
            f"elapsed_ms={elapsed_ms} "
            f"evidence_bytes={diagnostics['evidence_bytes']} "
            f"approx_input_tokens={diagnostics['approx_input_tokens']} "
            "provider_response_id_received=False"
        )

    @classmethod
    def _log_provider_exception(cls, error: Exception, model: str, started_at: float) -> None:
        response = getattr(error, "response", None)
        headers = getattr(response, "headers", {}) or {}
        request_id = getattr(error, "request_id", None) or headers.get("x-request-id")
        status_code = getattr(error, "status_code", None) or getattr(response, "status_code", None)
        error_code = getattr(error, "code", None)
        error_type = getattr(error, "type", None)
        elapsed_ms = round((perf_counter() - started_at) * 1000)
        print(
            "Replay Coach provider exception: "
            f"reason={cls._provider_exception_reason(error, status_code)} "
            f"exception_class={type(error).__name__} "
            f"http_status={status_code} "
            f"provider_error_code={error_code} "
            f"provider_error_type={error_type} "
            f"provider_message={cls._sanitize_provider_message(error)} "
            f"provider_request_id={request_id} "
            f"model={model} method=responses.create "
            f"elapsed_ms={elapsed_ms} schema_name={cls.SCHEMA_NAME}"
        )

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
    def _log_response_received(response_id: Any, status: str, output_text: Any, usage: Dict[str, Any]) -> None:
        length = len(output_text) if isinstance(output_text, str) else 0
        print(
            "Replay Coach provider response received: "
            f"provider_response_id_present={bool(response_id)} "
            f"status={status} output_text_length={length} "
            f"model={usage['model']} input_tokens={usage['input_tokens']} "
            f"output_tokens={usage['output_tokens']} total_tokens={usage['total_tokens']} "
            f"cached_input_tokens={usage['cached_input_tokens']} "
            f"reasoning_tokens={usage['reasoning_tokens']}"
        )

    @staticmethod
    def _log_response_diagnostic(reason: str, **fields: Any) -> None:
        values = " ".join(f"{name}={value}" for name, value in fields.items())
        print(f"Replay Coach response diagnostic: reason={reason} {values}".rstrip())

    @classmethod
    def _log_validation_error(cls, response_id: Any, status: str, error: ValidationError) -> None:
        sanitized_errors = [
            {"path": ".".join(str(part) for part in item["loc"]), "type": item["type"], "message": item["msg"]}
            for item in error.errors(include_url=False)
        ]
        cls._log_response_diagnostic(
            "COACH_SCHEMA_VALIDATION_FAILED",
            response_id=response_id,
            status=status,
            errors=sanitized_errors,
        )

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
        print(
            "Replay Coach baseline completed: "
            f"trade_date={context.get('trade_date')} "
            f"symbol={context.get('stock', {}).get('symbol')} "
            f"provider_response_id={response_id} "
            f"model={usage['model']} "
            f"input_tokens={usage['input_tokens']} "
            f"output_tokens={usage['output_tokens']} "
            f"total_tokens={usage['total_tokens']} "
            f"cached_input_tokens={usage['cached_input_tokens']} "
            f"reasoning_tokens={usage['reasoning_tokens']} "
            f"duration_ms={usage['duration_ms']} "
            f"evidence_bytes={usage['evidence_bytes']}"
        )

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
        schema = ProviderReplayCoachAnalysis.model_json_schema()

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
        return schema
