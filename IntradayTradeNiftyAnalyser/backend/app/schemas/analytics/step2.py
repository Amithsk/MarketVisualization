#IntradayTradeNiftyAnalyser/backend/app/schemas/analytics/step2.py

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ====================================================
# MARKET BEHAVIOR
# ====================================================

class MarketBehaviorSchema(BaseModel):
    trade_date: date
    index_open_behavior: str
    early_volatility: str
    market_participation: str
    trade_allowed: bool
    frozen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ====================================================
# MARKET OPEN BEHAVIOR
# ====================================================

class MarketOpenBehaviorSchema(BaseModel):
    trade_date: date
    ir_high: float
    ir_low: float
    ir_range: float
    ir_ratio: float

    volatility_state: str

    vwap_cross_count: int
    vwap_state: str

    range_hold_status: str

    trade_permission: str

    reason: str

    decision_locked_at: datetime
    created_at: datetime


# ====================================================
# MARKET VALIDATION
# ====================================================

class Step2MarketValidationSchema(BaseModel):
    trade_date: date

    trend_strength: float

    vwap_cross_count: int

    vwap_hold_percentage: float

    analysis_status: str

    rule_config_version: str

    created_at: datetime


# ====================================================
# RESPONSE
# ====================================================

class Step2ResponseSchema(BaseModel):
    trade_date: str

    market_behavior: Optional[MarketBehaviorSchema] = None

    market_open_behavior: Optional[MarketOpenBehaviorSchema] = None

    market_validation: Optional[Step2MarketValidationSchema] = None