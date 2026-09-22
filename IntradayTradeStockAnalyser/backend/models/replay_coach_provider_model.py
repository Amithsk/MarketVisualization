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


class ProviderReplayCoachTransport(CoachModel):
    executed_trade_analysis: ExecutedTradeAnalysis
    alternative_trade_plans: ProviderAlternativeTradePlans
    key_learning: KeyLearning
    limitations: list[str]
