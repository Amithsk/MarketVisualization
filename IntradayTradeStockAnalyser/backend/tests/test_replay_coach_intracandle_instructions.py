from backend.services.replay_coach_follow_up_openai_service import FOLLOW_UP_COACH_INSTRUCTIONS, FOLLOW_UP_PROMPT_VERSION
from backend.services.replay_coach_openai_service import ReplayCoachOpenAIService


def test_original_instructions_make_intracandle_execution_neutral_and_no_lookahead():
    instructions = ReplayCoachOpenAIService.SYSTEM_INSTRUCTIONS
    assert ReplayCoachOpenAIService.PROMPT_VERSION == "replay_coach_prompt_v12"
    assert "observation, not evidence of a weak or premature entry" in instructions
    assert "strategy label" in instructions
    assert "unknown and neutral" in instructions
    assert "execution/fill-like time" in instructions
    assert "final OHLC, volume, VWAP" in instructions
    assert "exact documented rule and evidence" in instructions


def test_follow_up_instructions_recheck_biased_entry_questions():
    assert FOLLOW_UP_PROMPT_VERSION == "replay_coach_follow_up_v4"
    assert "neutral by itself" in FOLLOW_UP_COACH_INSTRUCTIONS
    assert "conversational context, not independent proof" in FOLLOW_UP_COACH_INSTRUCTIONS
    assert "correct that assumption" in FOLLOW_UP_COACH_INSTRUCTIONS
    assert "Missing confirmation evidence is unknown and neutral" in FOLLOW_UP_COACH_INSTRUCTIONS
