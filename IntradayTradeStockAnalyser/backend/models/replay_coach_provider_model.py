"""Provider-only transport contract for Replay Coach structured output."""
from typing import Literal, Optional

from pydantic import Field

from backend.models.replay_coach_model import CoachModel, ExecutedTradeAnalysis, KeyLearning


class ProviderTradeAlternativePlan(CoachModel):
    direction: Literal["LONG", "SHORT"]
    entry: float
    stop: float
    target: float
    rating: int = Field(ge=1, le=10)
    reason: str = Field(min_length=1)
    trigger_condition: str = Field(min_length=1)
    invalidation_condition: str = Field(min_length=1)
    evidence_time: Optional[str]


class ProviderWaitAlternativePlan(CoachModel):
    rating: int = Field(ge=1, le=10)
    reason: str = Field(min_length=1)
    trigger_condition: str = Field(min_length=1)
    invalidation_condition: str = Field(min_length=1)
    evidence_time: Optional[str]


class ProviderNoTradeAlternativePlan(ProviderWaitAlternativePlan):
    pass


class ProviderAlternativeTradePlans(CoachModel):
    trade: ProviderTradeAlternativePlan
    wait: ProviderWaitAlternativePlan
    no_trade: ProviderNoTradeAlternativePlan

class ProviderBestFullSessionPlan(CoachModel):
    decision: Literal["TAKE"]
    trade_name: str = Field(min_length=1, max_length=120)
    direction: Literal["LONG", "SHORT"]
    opportunity_score: int = Field(ge=1, le=10)
    score_explanation: str = Field(min_length=1, max_length=600)
    market_story: str = Field(min_length=1, max_length=1200)
    setup_explanation: str = Field(min_length=1, max_length=1200)
    decision_time: str
    entry_trigger: str = Field(min_length=1, max_length=600)
    entry_price: float
    entry_price_upper: Optional[float] = None
    stop_price: float
    target_price: float
    invalidation_condition: str = Field(min_length=1, max_length=600)
    volume_explanation: str = Field(min_length=1, max_length=800)
    nifty_explanation: str = Field(min_length=1, max_length=800)
    beginner_lesson: str = Field(min_length=1, max_length=800)
    decision_evidence_times: list[str] = Field(default_factory=list, max_length=12)
    outcome_evidence_times: list[str] = Field(default_factory=list, max_length=12)


class ProviderReplayCoachTransport(CoachModel):
    executed_trade_analysis: ExecutedTradeAnalysis
    best_full_session_plan: ProviderBestFullSessionPlan
    key_learning: KeyLearning
    limitations: list[str]
