//IntradayTradeStockAnalyser/frontend/types/replay.ts

import { Candle } from "./candle";

export type ReplayTradeData = {

    strategy: string;

    position_type: string;

    trade_mode: string;

    setup_description: string;

    planned_entry_price: number;

    planned_stop_price: number;

    planned_target_price: number;

    plan_status: string;
};

export type MarketContext = {

    preopen_price: number | null;

    gap_pct: number | null;

    gap_class: string | null;

    prior_range_size: string | null;

    prior_day_overlap: string | null;

    prior_structure_state: string | null;

    final_market_context: string | null;

    final_reason: string | null;
};

export type MarketBehavior = {

    index_open_behavior: string | null;

    early_volatility: string | null;

    market_participation: string | null;

    trade_allowed: boolean | null;
};

export type MarketOpenBehavior = {

    ir_high: number | null;

    ir_low: number | null;

    ir_range: number | null;

    ir_ratio: number | null;

    volatility_state: string | null;

    vwap_cross_count: number | null;

    vwap_state: string | null;

    range_hold_status: string | null;

    trade_permission: string | null;

    reason: string | null;
};

export type ExecutionControl = {

    market_context: string | null;

    trade_permission: string | null;

    allowed_strategies: string[];

    max_trades_allowed: number | null;

    execution_allowed: boolean | null;
};

export type StockSelectionContext = {

    direction: string | null;

    strategy_used: string | null;

    rs_value: number | null;

    gap_high: number | null;

    gap_low: number | null;

    intraday_high: number | null;

    intraday_low: number | null;

    last_higher_low: number | null;

    yesterday_close: number | null;

    vwap_value: number | null;

    structure_valid: boolean | null;

    reason: string | null;

    tradable: boolean | null;

    rejection_tag: string | null;
};

export type TradeConstruction = {

    strategy_used: string | null;

    direction: string | null;

    structure_valid: boolean | null;

    entry_price: number | null;

    stop_loss: number | null;

    risk_per_share: number | null;

    quantity: number | null;

    target_price: number | null;

    trade_status: string | null;

    block_reason: string | null;
};

export type NarrativeContext = {

    market_summary: string | null;

    strategy_summary: string | null;

    execution_summary: string | null;

    relative_strength_summary: string | null;

    trade_construction_summary: string | null;

    learning_insight: string | null;
};

// ============================================
// MARKET EVENT TYPES
// ============================================

export type EventValidation = {

    above_vwap: boolean;

    volume_expansion: boolean;

    orb_valid: boolean;
};

export type NiftyContext = {

    direction: string;

    relative_strength_score: number;
};

export type MarketEvent = {

    event_id: number;

    trade_date: string;

    stock_symbol: string;

    candle_time: string;

    event_type: string;

    nifty_context: string | null;

    market_bias: string | null;

    strategy_relevance: string | null;

    relative_strength: string | null;

    vwap_relation: string | null;

    volume_expansion: boolean | null;

    breakout_strength: number | null;

    orb_related: boolean | null;

    event_severity: string | null;

    explanation?: string;

    trading_implication?: string;

    strength_score?: number;

    validation?: EventValidation;

    nifty_context_data?: NiftyContext;

    event_metadata?: Record<string, any>;

    candle_index?: number;

    price?: number;

    created_at?: string;
};
export type ReplayData = {

    trade_data: ReplayTradeData;

    stock_candles: Candle[];

    nifty_candles: Candle[];

    market_events: MarketEvent[];

    market_context: MarketContext;

    market_behavior: MarketBehavior;

    market_open_behavior: MarketOpenBehavior;

    execution_control: ExecutionControl;

    explanation_context?: {

        candle_explanations?: Record<string, unknown>;

        strategy_explanations?: {

            strategy_name?: string;

            explanation?: string;

            confidence_score?: number;

            tradable?: boolean;

            direction?: string;

        };

        timeline_narration?: unknown[];

        trade_coaching?: Record<string, unknown>;

        nifty_relationship_analysis?: Record<string, unknown>;
    };



    stock_selection_context: StockSelectionContext;

    trade_construction: TradeConstruction;

    narrative_context: NarrativeContext;
};