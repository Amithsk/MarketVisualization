"""Strict, provider-independent contract for a Replay Coach review."""
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class AlternativeTradePlan(CoachModel):
    name: str
    decision: Literal["TAKE", "WAIT", "NO_TRADE"]
    side: Optional[Literal["BUY", "SELL"]] = None
    entry_condition: str
    entry_price: Optional[float] = None
    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    risk: Optional[float] = None
    reward: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    rating: int = Field(ge=1, le=10)
    why_good: List[str]
    risks: List[str]
    evidence_times: List[str]

    @model_validator(mode="after")
    def validate_prices_and_calculations(self):
        values = (self.entry_price, self.stop_price, self.target_price,
                  self.risk, self.reward, self.risk_reward_ratio)
        if self.decision != "TAKE":
            if self.side is not None or any(value is not None for value in values):
                raise ValueError("WAIT and NO_TRADE plans must not contain side or price calculations.")
            return self
        if self.side is None or any(value is None for value in values):
            raise ValueError("TAKE plans require side, prices, risk, reward, and risk/reward ratio.")
        expected_risk = self.entry_price - self.stop_price if self.side == "BUY" else self.stop_price - self.entry_price
        expected_reward = self.target_price - self.entry_price if self.side == "BUY" else self.entry_price - self.target_price
        if expected_risk <= 0 or expected_reward <= 0:
            raise ValueError("TAKE plan has an invalid side, entry, stop, or target arrangement.")
        if abs(self.risk - expected_risk) > 0.000001 or abs(self.reward - expected_reward) > 0.000001:
            raise ValueError("TAKE plan risk and reward do not match its prices.")
        if abs(self.risk_reward_ratio - (expected_reward / expected_risk)) > 0.000001:
            raise ValueError("TAKE plan risk/reward ratio does not match its prices.")
        return self


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
        decisions = {plan.decision for plan in self.alternative_trade_plans}
        if not {"TAKE", "WAIT", "NO_TRADE"}.issubset(decisions):
            raise ValueError("Analysis must include TAKE, WAIT, and NO_TRADE alternatives.")
        return self
