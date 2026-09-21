"""Local, process-safe configuration loading for Replay Coach."""
from pathlib import Path

from dotenv import load_dotenv


# This module lives at <project>/backend/services, so parents[2] is the
# IntradayTradeStockAnalyser project directory regardless of the launch CWD.
PROJECT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_DIR / ".env"


def load_replay_coach_environment(env_file: Path = ENV_FILE) -> None:
    """Load local Coach settings without replacing explicit process values."""
    load_dotenv(env_file, override=False)


load_replay_coach_environment()
