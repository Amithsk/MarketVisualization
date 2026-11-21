# TradeJournal/backend/app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

# -------- Trade Plan --------

class TradePlanCreate(BaseModel):
    # ✅ NEW — symbol captured at planning time
    symbol: str

    plan_date: date
    trade_mode: str
    strategy: str
    position_type: str
    setup_description: str
    planned_entry_price: Optional[float]
    planned_stop_price: Optional[float]
    planned_target_price: Optional[float]
    planned_risk_amount: Optional[float]
    planned_position_size: int


class NotTakenPayload(BaseModel):
    not_taken_reason: str


# -------- Execution --------

class ExecuteTradePayload(BaseModel):
    entry_timestamp: Optional[datetime] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    client_request_id: Optional[str] = None


class AddTradePayload(BaseModel):
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)
    execution_timestamp: datetime
    note: str = Field(min_length=1, max_length=2000)
    client_request_id: Optional[str] = None


class ExitTradePayload(BaseModel):
    exit_price: float = Field(gt=0)
    exit_reason: str
    exit_timestamp: datetime
    quantity: Optional[int] = Field(default=None, gt=0)
    client_request_id: Optional[str] = None


# -------- Review --------

class TradeReviewPayload(BaseModel):
    # ✅ NEW — symbol stored with review
    symbol: str

    exit_reason: str
    followed_entry_rules: bool
    followed_stop_rules: bool
    followed_position_sizing: bool
    emotional_state: str
    market_context: str
    learning_insight: str
    trade_grade: str

# --------------------------------------------------
# TRADE PLAN RESPONSE STATE
# --------------------------------------------------

class TradeState(BaseModel):
    is_executed: bool
    is_exited: bool
    is_reviewed: bool


# --------------------------------------------------
# TRADE PLAN RESPONSE
# --------------------------------------------------

class TradePlanResponse(BaseModel):
    id: int

    trade_id: Optional[int]

    symbol: str

    plan_date: date
    trade_mode: str
    strategy: str
    position_type: str

    setup_description: str
    entry_trigger: Optional[str]

    planned_entry_price: Optional[float]
    planned_stop_price: Optional[float]
    planned_target_price: Optional[float]

    planned_risk_amount: Optional[float]
    planned_position_size: int

    plan_status: str

    not_taken_reason: Optional[str]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    trade_state: TradeState

    class Config:
        from_attributes = True
