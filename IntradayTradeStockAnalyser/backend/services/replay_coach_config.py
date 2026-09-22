"""Local, process-safe configuration loading for Replay Coach."""
from pathlib import Path
import os

from dotenv import load_dotenv


# This module lives at <project>/backend/services, so parents[2] is the
# IntradayTradeStockAnalyser project directory regardless of the launch CWD.
PROJECT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_DIR / ".env"


def load_replay_coach_environment(env_file: Path = ENV_FILE) -> None:
    """Load local Coach settings without replacing explicit process values."""
    load_dotenv(env_file, override=False)


DEFAULT_MAX_OUTPUT_TOKENS = 16000
MIN_MAX_OUTPUT_TOKENS = 8000
MAX_MAX_OUTPUT_TOKENS = 32000


def replay_coach_max_output_tokens() -> tuple[int, str]:
    """Return the validated Coach-only output cap and its safe source label."""
    raw = os.getenv("OPENAI_REPLAY_COACH_MAX_OUTPUT_TOKENS")
    if raw is None or not raw.strip():
        return DEFAULT_MAX_OUTPUT_TOKENS, "CODE_DEFAULT"
    try:
        value = int(raw)
    except ValueError as error:
        raise RuntimeError("OPENAI_REPLAY_COACH_MAX_OUTPUT_TOKENS must be an integer.") from error
    if not MIN_MAX_OUTPUT_TOKENS <= value <= MAX_MAX_OUTPUT_TOKENS:
        raise RuntimeError(f"OPENAI_REPLAY_COACH_MAX_OUTPUT_TOKENS must be between {MIN_MAX_OUTPUT_TOKENS} and {MAX_MAX_OUTPUT_TOKENS}.")
    return value, "ENV"


load_replay_coach_environment()
# Fail during backend import/startup rather than after a provider request.
replay_coach_max_output_tokens()
