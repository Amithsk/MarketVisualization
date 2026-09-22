"""Persisted and frontend-facing Replay Coach contracts.

Provider transport types deliberately live in ``replay_coach_provider_model``.
Keeping this model independent allows completed historical analyses to remain
readable while the provider contract evolves safely.
"""
from decimal import Decimal
from typing import Annotated, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer, model_validator

class CoachModel(BaseModel): model_config = ConfigDict(extra="forbid")
class Evidence(CoachModel):
    time: str; stock_values: str; market_values: str; calculation: Optional[str] = None
class ReviewPoint(CoachModel): point: str; evidence: List[Evidence]
class NegativeReviewPoint(ReviewPoint): why_it_matters: str
class Improvement(CoachModel): action: str; rule: str; example_using_this_trade: str
class ExecutedTradeAnalysis(CoachModel):
    summary: str; good: List[ReviewPoint]; bad: List[NegativeReviewPoint]; how_to_improve: List[Improvement]
class AlternativePlanBase(CoachModel):
    name: str; entry_condition: str; rating: int = Field(ge=1, le=10); why_good: List[str]; risks: List[str]; evidence_times: List[str]

class TradeAlternativePlan(AlternativePlanBase):
    plan_type: Literal["TRADE"]; side: Literal["BUY", "SELL"]
    entry_price: Decimal; stop_price: Decimal; target_price: Decimal
    numeric_explanation: str; invalidation_condition: str
    risk: Decimal; reward: Decimal; risk_reward_ratio: Decimal
    @field_serializer("entry_price", "stop_price", "target_price", "risk", "reward", "risk_reward_ratio", when_used="json")
    def serialize_decimal(self, value: Decimal) -> float: return float(value)
    @computed_field
    @property
    def decision(self) -> Literal["TAKE"]: return "TAKE"

class WaitAlternativePlan(AlternativePlanBase):
    plan_type: Literal["WAIT"]; confirmation_price: Optional[float] = None; confirmation_zone: Optional[str] = None
    candle_time_condition: str; numeric_explanation: str; immediate_execution_rejection: str
    @computed_field
    @property
    def decision(self) -> Literal["WAIT"]: return "WAIT"
    @computed_field
    @property
    def side(self) -> None: return None
    @computed_field
    @property
    def entry_price(self) -> None: return None
    @computed_field
    @property
    def stop_price(self) -> None: return None
    @computed_field
    @property
    def target_price(self) -> None: return None
    @computed_field
    @property
    def risk(self) -> None: return None
    @computed_field
    @property
    def reward(self) -> None: return None
    @computed_field
    @property
    def risk_reward_ratio(self) -> None: return None

class NoTradeAlternativePlan(AlternativePlanBase):
    plan_type: Literal["NO_TRADE"]; numeric_reasons: List[str]; invalidating_market_stock_conditions: List[str]; reconsideration_condition: Optional[str] = None
    @computed_field
    @property
    def decision(self) -> Literal["NO_TRADE"]: return "NO_TRADE"
    @computed_field
    @property
    def side(self) -> None: return None
    @computed_field
    @property
    def entry_price(self) -> None: return None
    @computed_field
    @property
    def stop_price(self) -> None: return None
    @computed_field
    @property
    def target_price(self) -> None: return None
    @computed_field
    @property
    def risk(self) -> None: return None
    @computed_field
    @property
    def reward(self) -> None: return None
    @computed_field
    @property
    def risk_reward_ratio(self) -> None: return None

AlternativeTradePlan = Annotated[Union[TradeAlternativePlan, WaitAlternativePlan, NoTradeAlternativePlan], Field(discriminator="plan_type")]
class KeyLearning(CoachModel): lesson: str; numeric_rule: str; example_using_this_trade: str
class ReplayCoachAnalysis(CoachModel):
    executed_trade_analysis: ExecutedTradeAnalysis
    alternative_trade_plans: List[AlternativeTradePlan]
    key_learning: KeyLearning
    limitations: List[str]
