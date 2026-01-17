# app/schemas.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

# -------- Trade Plan --------

class TradePlanCreate(BaseModel):
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
    symbol: str
    side: str
    quantity: int
    entry_price: float
    entry_timestamp: datetime


class ExitTradePayload(BaseModel):
    exit_price: float
    exit_reason: str
    exit_timestamp: datetime


# -------- Review --------

class TradeReviewPayload(BaseModel):
    exit_reason: str
    followed_entry_rules: bool
    followed_stop_rules: bool
    followed_position_sizing: bool
    emotional_state: str
    market_context: str
    learning_insight: str
    trade_grade: str



    
