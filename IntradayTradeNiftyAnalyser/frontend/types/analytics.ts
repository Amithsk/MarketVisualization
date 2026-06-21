//IntradayTradeNiftyAnalyser/frontend/types/analytics.ts
// =====================================================
// STEP 1
// =====================================================

export interface Step1Context {
    trade_date: string;
    preopen_price: number;
    gap_pct: number;
    gap_class: string;
    prior_range_size: string;
    prior_day_overlap: string;
    prior_structure_state: string;
    final_market_context: string;
    final_reason: string;
    created_at: string;
}

export interface MarketValidation {
    trade_date: string;
    day_type: string | null;
    trend_strength: number;
    total_range: number;
    net_move: number;
    pullback_depth: number;
    vwap_cross_count: number;
    vwap_hold_percentage: number;
    analysis_status: string;
    rule_config_version: string;
    created_at: string;
}

export interface Step1Response {
    trade_date: string;
    step1_context: Step1Context | null;
    market_validation: MarketValidation | null;
}


// =====================================================
// STEP 2
// =====================================================

export interface MarketBehavior {
    trade_date: string;
    index_open_behavior: string;
    early_volatility: string;
    market_participation: string;
    trade_allowed: boolean;
    frozen_at: string;
    created_at: string;
    updated_at: string;
}

export interface MarketOpenBehavior {
    trade_date: string;
    ir_high: number;
    ir_low: number;
    ir_range: number;
    ir_ratio: number;

    volatility_state: string;

    vwap_cross_count: number;
    vwap_state: string;

    range_hold_status: string;

    trade_permission: string;

    reason: string;

    decision_locked_at: string;
    created_at: string;
}

export interface Step2Validation {
    trade_date: string;
    trend_strength: number;
    vwap_cross_count: number;
    vwap_hold_percentage: number;
    analysis_status: string;
    rule_config_version: string;
    created_at: string;
}

export interface Step2Response {
    trade_date: string;

    market_behavior: MarketBehavior | null;

    market_open_behavior: MarketOpenBehavior | null;

    market_validation: Step2Validation | null;
}


// =====================================================
// PERFORMANCE
// =====================================================

export interface ExecutionControl {
    trade_date: string;

    market_context: string;

    trade_permission: string;

    allowed_strategies: string;

    max_trades_allowed: number;

    execution_allowed: boolean;

    decided_at: string;

    created_at: string;
}

export interface StockSelection {
    trade_date: string;

    symbol: string;

    direction: string;

    strategy_used: string;

    rs_value: number | null;

    gap_high: number | null;
    gap_low: number | null;

    intraday_high: number | null;
    intraday_low: number | null;

    last_higher_low: number | null;

    yesterday_close: number | null;

    vwap_value: number | null;

    structure_valid: boolean;

    tradable: boolean;

    rejection_tag: string | null;

    reason: string;

    evaluated_at: string;

    created_at: string;
}

export interface PerformanceMetrics {
    trade_date: string;

    candidate_count: number | null;

    selected_count: number | null;

    total_success: number | null;

    total_failure: number | null;

    total_missed_opportunities: number | null;

    conversion_rate: number | null;

    failure_rate: number | null;

    missed_opportunity_rate: number | null;

    analysis_status: string | null;

    rule_config_version: string | null;

    created_at: string | null;
}

export interface PerformanceResponse {
    trade_date: string;

    execution_control: ExecutionControl | null;

    stock_selection: StockSelection[];

    performance_metrics: PerformanceMetrics | null;
}


// =====================================================
// LEARNING
// =====================================================

export interface Summary {
    trade_date: string;

    summary_text: string;

    analysis_status: string;

    rule_config_version: string;

    created_at: string;
}

export interface Suggestion {
    trade_date: string;

    rule_name: string;

    current_value: number;

    suggested_value: number;

    support_metric: string;

    impact: number;

    confidence: number;

    priority: string;

    created_at: string;
}

export interface JobStatus {
    execution_id: string;

    trade_date: string;

    status: string;

    start_time: string;

    end_time: string | null;

    last_updated_at: string;
}

export interface LearningResponse {
    trade_date: string;

    summary: Summary | null;

    suggestions: Suggestion[];

    job_status: JobStatus | null;
}