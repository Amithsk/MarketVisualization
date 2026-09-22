"""Manual, opt-in metadata diagnostics. Never prints response/input content."""
import argparse
import os
from backend.services.replay_coach_openai_service import ReplayCoachOpenAIService

def summary(response):
    usage = getattr(response, "usage", None)
    details = getattr(response, "incomplete_details", None)
    error = getattr(response, "error", None)
    output = getattr(response, "output", None) or []
    return {"response_id": getattr(response, "id", None), "status": getattr(response, "status", None), "model": getattr(response, "model", None), "max_output_tokens": getattr(response, "max_output_tokens", None), "incomplete_reason": getattr(details, "reason", None), "usage_present": usage is not None, "input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None), "total_tokens": getattr(usage, "total_tokens", None), "error_present": error is not None, "error_type": type(error).__name__ if error else None, "error_code": getattr(error, "code", None), "output_item_count": len(output), "output_item_types": [type(item).__name__ for item in output], "output_text_length": len(getattr(response, "output_text", "") or ""), "created_at": getattr(response, "created_at", None), "completed_at": getattr(response, "completed_at", None)}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("response_id")
    args = parser.parse_args(); key = os.getenv("OPENAI_API_KEY")
    if not key: raise SystemExit("OPENAI_API_KEY is required.")
    client = ReplayCoachOpenAIService._client(key, ReplayCoachOpenAIService._timeout_seconds())
    print(summary(client.responses.retrieve(args.response_id)))

if __name__ == "__main__": main()
