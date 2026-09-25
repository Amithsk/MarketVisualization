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
class FullSessionPlan(CoachModel):
    decision: Literal["TAKE", "WAIT", "NO_TRADE"]; trade_name: str; direction: Literal["LONG", "SHORT", "NEUTRAL"]; opportunity_score: int
    score_explanation: str; market_story: str; setup_explanation: str; decision_time: Optional[str] = None; entry_trigger: str
    entry_price: Optional[float] = None; entry_price_upper: Optional[float] = None; stop_price: Optional[float] = None; target_price: Optional[float] = None
    risk: Optional[float] = None; reward: Optional[float] = None; reward_to_risk: Optional[float] = None; required_reward_to_risk: float = 4.0; ratio_status: str
    invalidation_condition: str; volume_explanation: str; nifty_explanation: str; beginner_lesson: str
    decision_evidence_times: List[str] = []; outcome_evidence_times: List[str] = []
class ReplayCoachAnalysis(CoachModel):
    executed_trade_analysis: ExecutedTradeAnalysis
    best_full_session_plan: Optional[FullSessionPlan] = None
    key_learning: KeyLearning
    limitations: List[str]

class CoachDisplayRow(CoachModel):
    component: str; value: str; rating: int; rating_max: int = 10
    explanation: str; graph_times: List[str]; status: str
class CoachDisplaySection(CoachModel):
    title: str; decision: str; overall_rating: int; valid: bool; rows: List[CoachDisplayRow]
class ExecutedTradeVerdictRow(CoachModel):
    component: str; value: str; meaning: str
class ExecutedTradeVerdict(CoachModel):
    title: str = "Executed Trade Verdict"; outcome_status: str; plan_standard_status: str
    rows: List[ExecutedTradeVerdictRow]
class DecisionQualityComponent(CoachModel):
    component: str; label: str; score: int; maximum_score: int; status: str
    observed_value: str; baseline: str; calculation: str; beginner_explanation: str
    improvement_condition: str; graph_times: List[str]
class DecisionQualityScore(CoachModel):
    score_version: str; overall_score: int; maximum_score: int; summary: str
    components: List[DecisionQualityComponent]
class TradeResultDisplay(CoachModel):
    status: str; pnl_amount: Optional[float] = None; summary: str
class NextTradeFocus(CoachModel):
    component: str; current_score: int; target_score: int; message: str
class CoachDisplay(CoachModel):
    presentation_version: str = "replay_coach_display_v2"
    trade_result: TradeResultDisplay
    decision_quality_score: DecisionQualityScore
    executed_trade_verdict: ExecutedTradeVerdict
    best_full_session_plan: Optional[FullSessionPlan] = None
    next_trade_focus: NextTradeFocus
    shared_graph_times: List[str] = []
    execution_times: dict[str, str] = {}
    detailed_evidence_available: bool = True
