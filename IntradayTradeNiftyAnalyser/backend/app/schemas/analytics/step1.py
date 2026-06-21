#IntradayTradeNiftyAnalyser/backend/app/schemas/analytics/step1.py

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Step1ContextSchema(BaseModel):
    trade_date: date
    preopen_price: float
    gap_pct: float
    gap_class: str
    prior_range_size: str
    prior_day_overlap: str
    prior_structure_state: str
    final_market_context: str
    final_reason: str
    created_at: datetime


class MarketValidationSchema(BaseModel):
    trade_date: date
    day_type: Optional[str] = None
    trend_strength: float
    total_range: float
    net_move: float
    pullback_depth: float
    vwap_cross_count: int
    vwap_hold_percentage: float
    analysis_status: str
    rule_config_version: str
    created_at: datetime


class Step1ResponseSchema(BaseModel):
    trade_date: str
    step1_context: Optional[Step1ContextSchema] = None
    market_validation: Optional[MarketValidationSchema] = None