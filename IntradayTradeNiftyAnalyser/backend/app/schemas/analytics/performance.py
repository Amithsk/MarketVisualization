#IntradayTradeNiftyAnalyser/backend/app/schemas/analytics/performance.py

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ====================================================
# EXECUTION CONTROL
# ====================================================

class ExecutionControlSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: date
    market_context: str
    trade_permission: str
    allowed_strategies: str
    max_trades_allowed: int
    execution_allowed: bool
    decided_at: datetime
    created_at: datetime


# ====================================================
# STOCK SELECTION
# ====================================================

class StockSelectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: date

    symbol: str

    direction: str

    strategy_used: str

    rs_value: Optional[float] = None

    gap_high: Optional[float] = None
    gap_low: Optional[float] = None

    intraday_high: Optional[float] = None
    intraday_low: Optional[float] = None

    last_higher_low: Optional[float] = None

    yesterday_close: Optional[float] = None

    vwap_value: Optional[float] = None

    structure_valid: bool

    tradable: bool

    rejection_tag: Optional[str] = None

    reason: str

    evaluated_at: datetime

    created_at: datetime


# ====================================================
# PERFORMANCE METRICS
# ====================================================

class PerformanceMetricsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: date

    candidate_count: Optional[int] = None

    selected_count: Optional[int] = None

    total_success: Optional[int] = None

    total_failure: Optional[int] = None

    total_missed_opportunities: Optional[int] = None

    conversion_rate: Optional[float] = None

    failure_rate: Optional[float] = None

    missed_opportunity_rate: Optional[float] = None

    analysis_status: Optional[str] = None

    rule_config_version: Optional[str] = None

    created_at: Optional[datetime] = None


# ====================================================
# RESPONSE
# ====================================================

class PerformanceResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: str

    execution_control: Optional[ExecutionControlSchema] = None

    stock_selection: list[StockSelectionSchema] = []

    performance_metrics: Optional[PerformanceMetricsSchema] = None