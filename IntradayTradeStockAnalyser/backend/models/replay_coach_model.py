"""Strict, provider-independent contract for a Replay Coach review."""
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class CoachModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(CoachModel):
    time: str
    stock_values: str
    market_values: str
    calculation: Optional[str] = None


class ReviewPoint(CoachModel):
    point: str
    evidence: List[Evidence]


class NegativeReviewPoint(ReviewPoint):
    why_it_matters: str


class Improvement(CoachModel):
    action: str
    rule: str
    example_using_this_trade: str


class ExecutedTradeAnalysis(CoachModel):
    summary: str
    good: List[ReviewPoint]
    bad: List[NegativeReviewPoint]
    how_to_improve: List[Improvement]


class AlternativePlanBase(CoachModel):
    name: str
    entry_condition: str
    rating: int = Field(ge=1, le=10)
    why_good: List[str]
    risks: List[str]
    evidence_times: List[str]


class TradeAlternativePlan(AlternativePlanBase):
    plan_type: Literal["TRADE"]
    side: Literal["BUY", "SELL"]
    entry_price: float
    stop_price: float
    target_price: float
    risk: float
    reward: float
    risk_reward_ratio: float
    numeric_explanation: str
    invalidation_condition: str

    @model_validator(mode="after")
    def validate_prices_and_calculations(self):
        expected_risk = self.entry_price - self.stop_price if self.side == "BUY" else self.stop_price - self.entry_price
        expected_reward = self.target_price - self.entry_price if self.side == "BUY" else self.entry_price - self.target_price
        if expected_risk <= 0 or expected_reward <= 0:
            raise ValueError("TAKE plan has an invalid side, entry, stop, or target arrangement.")
        if abs(self.risk - expected_risk) > 0.000001 or abs(self.reward - expected_reward) > 0.000001:
            raise ValueError("TAKE plan risk and reward do not match its prices.")
        if abs(self.risk_reward_ratio - (expected_reward / expected_risk)) > 0.000001:
            raise ValueError("TAKE plan risk/reward ratio does not match its prices.")
        return self

    @computed_field
    @property
    def decision(self) -> Literal["TAKE"]:
        return "TAKE"


class WaitAlternativePlan(AlternativePlanBase):
    plan_type: Literal["WAIT"]
    confirmation_price: Optional[float] = None
    confirmation_zone: Optional[str] = None
    candle_time_condition: str
    numeric_explanation: str
    immediate_execution_rejection: str

    @computed_field
    @property
    def decision(self) -> Literal["WAIT"]:
        return "WAIT"

    @computed_field
    @property
    def side(self) -> None:
        return None

    @computed_field
    @property
    def entry_price(self) -> None:
        return None

    @computed_field
    @property
    def stop_price(self) -> None:
        return None

    @computed_field
    @property
    def target_price(self) -> None:
        return None

    @computed_field
    @property
    def risk(self) -> None:
        return None

    @computed_field
    @property
    def reward(self) -> None:
        return None

    @computed_field
    @property
    def risk_reward_ratio(self) -> None:
        return None


class NoTradeAlternativePlan(AlternativePlanBase):
    plan_type: Literal["NO_TRADE"]
    numeric_reasons: List[str]
    invalidating_market_stock_conditions: List[str]
    reconsideration_condition: Optional[str] = None

    @computed_field
    @property
    def decision(self) -> Literal["NO_TRADE"]:
        return "NO_TRADE"

    @computed_field
    @property
    def side(self) -> None:
        return None

    @computed_field
    @property
    def entry_price(self) -> None:
        return None

    @computed_field
    @property
    def stop_price(self) -> None:
        return None

    @computed_field
    @property
    def target_price(self) -> None:
        return None

    @computed_field
    @property
    def risk(self) -> None:
        return None

    @computed_field
    @property
    def reward(self) -> None:
        return None

    @computed_field
    @property
    def risk_reward_ratio(self) -> None:
        return None


AlternativeTradePlan = Annotated[
    Union[TradeAlternativePlan, WaitAlternativePlan, NoTradeAlternativePlan],
    Field(discriminator="plan_type"),
]


class KeyLearning(CoachModel):
    lesson: str
    numeric_rule: str
    example_using_this_trade: str


class ReplayCoachAnalysis(CoachModel):
    executed_trade_analysis: ExecutedTradeAnalysis
    alternative_trade_plans: List[AlternativeTradePlan]
    key_learning: KeyLearning
    limitations: List[str]

    @model_validator(mode="after")
    def require_learning_alternatives(self):
        decisions = {plan.plan_type for plan in self.alternative_trade_plans}
        if not {"TRADE", "WAIT", "NO_TRADE"}.issubset(decisions):
            raise ValueError("Analysis must include TRADE, WAIT, and NO_TRADE alternatives.")
        return self
