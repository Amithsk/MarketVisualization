#IntradayTradeStockAnalyser/backend/models/replay_response.py

from typing import (
    List,
    Optional,
    Any
)

from pydantic import BaseModel


class MarketContextResponse(BaseModel):

    preopen_price: Optional[float] = None

    gap_pct: Optional[float] = None

    gap_class: Optional[str] = None

    prior_range_size: Optional[str] = None

    prior_day_overlap: Optional[str] = None

    prior_structure_state: Optional[str] = None

    final_market_context: Optional[str] = None

    final_reason: Optional[str] = None


class MarketBehaviorResponse(BaseModel):

    index_open_behavior: Optional[str] = None

    early_volatility: Optional[str] = None

    market_participation: Optional[str] = None

    trade_allowed: Optional[bool] = None


class MarketOpenBehaviorResponse(BaseModel):

    ir_high: Optional[float] = None

    ir_low: Optional[float] = None

    ir_range: Optional[float] = None

    ir_ratio: Optional[float] = None

    volatility_state: Optional[str] = None

    vwap_cross_count: Optional[int] = None

    vwap_state: Optional[str] = None

    range_hold_status: Optional[str] = None

    trade_permission: Optional[str] = None

    reason: Optional[str] = None


class ExecutionControlResponse(BaseModel):

    market_context: Optional[str] = None

    trade_permission: Optional[str] = None

    allowed_strategies: List[str] = []

    max_trades_allowed: Optional[int] = None

    execution_allowed: Optional[bool] = None


class StockSelectionContextResponse(BaseModel):

    direction: Optional[str] = None

    strategy_used: Optional[str] = None

    rs_value: Optional[float] = None

    gap_high: Optional[float] = None

    gap_low: Optional[float] = None

    intraday_high: Optional[float] = None

    intraday_low: Optional[float] = None

    last_higher_low: Optional[float] = None

    yesterday_close: Optional[float] = None

    vwap_value: Optional[float] = None

    structure_valid: Optional[bool] = None

    reason: Optional[str] = None

    tradable: Optional[bool] = None

    rejection_tag: Optional[str] = None


class TradeConstructionResponse(BaseModel):

    strategy_used: Optional[str] = None

    direction: Optional[str] = None

    structure_valid: Optional[bool] = None

    entry_price: Optional[float] = None

    stop_loss: Optional[float] = None

    risk_per_share: Optional[float] = None

    quantity: Optional[int] = None

    target_price: Optional[float] = None

    trade_status: Optional[str] = None

    block_reason: Optional[str] = None


class NarrativeContextResponse(BaseModel):

    market_summary: Optional[str] = None

    strategy_summary: Optional[str] = None

    execution_summary: Optional[str] = None

    relative_strength_summary: Optional[str] = None

    trade_construction_summary: Optional[str] = None

    learning_insight: Optional[str] = None


class ReplayResponse(BaseModel):

    trade_data: dict

    stock_candles: List[Any]

    nifty_candles: List[Any]

    market_context: MarketContextResponse

    market_behavior: MarketBehaviorResponse

    market_open_behavior: MarketOpenBehaviorResponse

    execution_control: ExecutionControlResponse

    stock_selection_context: StockSelectionContextResponse

    trade_construction: TradeConstructionResponse

    narrative_context: NarrativeContextResponse