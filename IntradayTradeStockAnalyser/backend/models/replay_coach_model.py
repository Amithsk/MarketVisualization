"""Provider and application contracts for a Replay Coach review."""
from decimal import Decimal, ROUND_HALF_UP
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

class ProviderTradeAlternativePlan(AlternativePlanBase):
    """Only non-derived trade inputs are accepted from the provider."""
    plan_type: Literal["TRADE"]; side: Literal["BUY", "SELL"]
    entry_price: Decimal; stop_price: Decimal; target_price: Decimal
    numeric_explanation: str; invalidation_condition: str

class TradeAlternativePlan(ProviderTradeAlternativePlan):
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

ProviderAlternativeTradePlan = Annotated[Union[ProviderTradeAlternativePlan, WaitAlternativePlan, NoTradeAlternativePlan], Field(discriminator="plan_type")]
AlternativeTradePlan = Annotated[Union[TradeAlternativePlan, WaitAlternativePlan, NoTradeAlternativePlan], Field(discriminator="plan_type")]
class KeyLearning(CoachModel): lesson: str; numeric_rule: str; example_using_this_trade: str
class ProviderReplayCoachAnalysis(CoachModel):
    executed_trade_analysis: ExecutedTradeAnalysis; alternative_trade_plans: List[ProviderAlternativeTradePlan]; key_learning: KeyLearning; limitations: List[str]
    @model_validator(mode="after")
    def require_learning_alternatives(self):
        if not {"TRADE", "WAIT", "NO_TRADE"}.issubset({plan.plan_type for plan in self.alternative_trade_plans}): raise ValueError("Analysis must include TRADE, WAIT, and NO_TRADE alternatives.")
        return self
class ReplayCoachAnalysis(ProviderReplayCoachAnalysis): alternative_trade_plans: List[AlternativeTradePlan]

MONEY_QUANTUM, RATIO_QUANTUM = Decimal("0.0001"), Decimal("0.0001")
def to_application_analysis(provider: ProviderReplayCoachAnalysis) -> ReplayCoachAnalysis:
    """Calculate arithmetic using Decimal and four-decimal ROUND_HALF_UP policy."""
    plans = []
    for plan in provider.alternative_trade_plans:
        if not isinstance(plan, ProviderTradeAlternativePlan): plans.append(plan); continue
        entry, stop, target = plan.entry_price, plan.stop_price, plan.target_price
        if plan.side == "BUY":
            if not stop < entry < target: raise ValueError("BUY TRADE requires stop_price < entry_price < target_price.")
            risk, reward = entry - stop, target - entry
        else:
            if not target < entry < stop: raise ValueError("SELL TRADE requires target_price < entry_price < stop_price.")
            risk, reward = stop - entry, entry - target
        if risk <= 0: raise ValueError("TRADE plan risk must be positive.")
        risk = risk.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP); reward = reward.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
        ratio = (reward / risk).quantize(RATIO_QUANTUM, rounding=ROUND_HALF_UP)
        # Replace provider prose so displayed arithmetic cannot contradict these values.
        explanation = f"Backend-calculated risk {risk:f}, reward {reward:f}, R:R {ratio:f}."
        values = plan.model_dump(); values["numeric_explanation"] = explanation
        plans.append(TradeAlternativePlan(**values, risk=risk, reward=reward, risk_reward_ratio=ratio))
    return ReplayCoachAnalysis(executed_trade_analysis=provider.executed_trade_analysis, alternative_trade_plans=plans, key_learning=provider.key_learning, limitations=provider.limitations)
