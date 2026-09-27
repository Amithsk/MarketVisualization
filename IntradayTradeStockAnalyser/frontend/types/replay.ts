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

export type ExecutedTrade = {
    trade_plan_id: number;
    trade_id: number;
    symbol: string;
    side: "BUY" | "SELL";
    entry_price: number;
    entry_timestamp: string;
    exit_price: number | null;
    exit_timestamp: string | null;
    quantity: number;
    status: string;
    pnl_amount: number | null;
    pnl_pct: number | null;
    trade_result: string | null;
    exit_reason: string | null;
    order_id: string | null;
    execution_source: "TRADE_JOURNAL";
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

export type CandleExplanation = {

    title?: string;

    summary?: string;

    reasons?: string[];

    market_interpretation?: string;

    trade_implication?: string;

    nifty_relationship?: string;

    confidence_score?: number;

    stock_analysis?: any;

    nifty_analysis?: any;

    relationship_analysis?: any;

    action?: any;

    learning?: any;
};

export type TimelineNarration = {

    candle_index: number;

    timestamp: string;

    title: string;

    nifty_behavior: string;

    stock_behavior: string;

    relationship: string;

    interpretation: string;

    trading_implication: string;
};
export type TradeCoaching = {

    execution_quality: string;

    entry_review: string;

    stop_review: string;

    exit_review: string;

    strategy_review: string;

    mistakes_detected: string[];

    improvement_suggestions: string[];

    confidence_score: number;
};

export type NiftyRelationshipAnalysis = {

    market_direction: string;

    stock_behavior: string;

    relationship_strength: string;

    market_alignment: string;

    relative_strength_analysis: string;

    trading_implication: string;

    confidence_score: number;
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

    executed_trade: ExecutedTrade;

    stock_candles: Candle[];

    nifty_candles: Candle[];

    market_events: MarketEvent[];

    market_context: MarketContext;

    market_behavior: MarketBehavior;

    market_open_behavior: MarketOpenBehavior;

    execution_control: ExecutionControl;

    explanation_context?: {

        candle_explanations?: Record<
            string,
            CandleExplanation
        >;

        strategy_explanations?: {

            strategy_name?: string;

            strategy_bias?: string;

            selection_reasons?: string[];

            market_alignment?: string;

            execution_expectation?: string;

            risk_notes?: string[];

            confidence_score?: number;

        };

        timeline_narration?: TimelineNarration[];

        trade_coaching?: TradeCoaching;

        nifty_relationship_analysis?: NiftyRelationshipAnalysis;
    };



    stock_selection_context: StockSelectionContext;

    trade_construction: TradeConstruction;

    narrative_context: NarrativeContext;
};

export type CoachEvidence = {
    time: string;
    stock_values: string;
    market_values: string;
    calculation: string | null;
};

export type CoachPoint = {
    point: string;
    evidence: CoachEvidence[];
    why_it_matters?: string;
};

export type ExecutedTradeAnalysis = {
    summary: string;
    good: CoachPoint[];
    bad: CoachPoint[];
    how_to_improve: { action: string; rule: string; example_using_this_trade: string }[];
};

export type AlternativeTradePlan = {
    name: string;
    decision: "TAKE" | "WAIT" | "NO_TRADE";
    side: "BUY" | "SELL" | null;
    entry_condition: string;
    entry_price: number | null;
    stop_price: number | null;
    target_price: number | null;
    risk: number | null;
    reward: number | null;
    risk_reward_ratio: number | null;
    rating: number;
    why_good: string[];
    risks: string[];
    evidence_times: string[];
};

export type KeyLearning = { lesson: string; numeric_rule: string; example_using_this_trade: string };

export type CoachAnalysis = {
    executed_trade_analysis: ExecutedTradeAnalysis;
    best_full_session_plan?: FullSessionPlan | null;
    key_learning: KeyLearning;
    limitations: string[];
};
export type CoachDisplayRow = { component: string; value: string; rating: number; rating_max: number; explanation: string; graph_times: string[]; status: string };
export type CoachDisplaySection = { title: string; decision: string; overall_rating: number; valid: boolean; rows: CoachDisplayRow[] };
export type FullSessionPlan = { decision: "TAKE" | "WAIT" | "NO_TRADE"; trade_name: string; direction: "LONG" | "SHORT" | "NEUTRAL"; opportunity_score: number; score_explanation: string; market_story: string; setup_explanation: string; decision_time: string | null; entry_trigger: string; entry_price: number | null; entry_price_upper: number | null; stop_price: number | null; target_price: number | null; risk: number | null; reward: number | null; reward_to_risk: number | null; required_reward_to_risk: number; ratio_status: string; invalidation_condition: string; volume_explanation: string; nifty_explanation: string; beginner_lesson: string; decision_evidence_times: string[]; outcome_evidence_times: string[] };
export type ExecutedTradeVerdict = { title: string; outcome_status: string; plan_standard_status: string; rows: { component: string; value: string; meaning: string }[] };
export type DecisionQualityComponent = { component: string; label: string; score: number; maximum_score: number; status: string; observed_value: string; baseline: string; calculation: string; beginner_explanation: string; improvement_condition: string; graph_times: string[] };
export type CoachDisplay = {
    presentation_version: string;
    trade_result: { status: string; pnl_amount: number | null; summary: string };
    decision_quality_score: { score_version: string; overall_score: number; maximum_score: number; summary: string; components: DecisionQualityComponent[] };
    next_trade_focus: { component: string; current_score: number; target_score: number; message: string };
    shared_graph_times: string[];
    execution_times: { entry?: string; exit?: string };
    executed_trade_verdict: ExecutedTradeVerdict; best_full_session_plan?: FullSessionPlan | null; detailed_evidence_available: boolean;
};

export type ReplayCoachStartResponse = {
    status: "success";
    coach_session_id: string;
    openai_response_id: string;
    trade_date: string;
    stock: string;
    analysis_id: number;
    analysis: CoachAnalysis;
    coach_display: CoachDisplay;
};

export type ReplayCoachMessageRole = "USER" | "ASSISTANT";
export type ReplayCoachMessageStatus = "PROCESSING" | "COMPLETED" | "FAILED";
export type ReplayCoachFollowUpIntent = "EXECUTED_TRADE_EXPLANATION" | "FULL_SESSION_PLAN_EXPLANATION" | "PLAN_COMPARISON" | "CALCULATION_EXPLANATION" | "CHART_EVIDENCE" | "TRADING_CONCEPT" | "NEXT_TRADE_LESSON" | "CLARIFICATION_REQUIRED" | "GENERAL_FOLLOW_UP";
export type ReplayCoachFeedbackRating = "HELPFUL" | "NEEDS_IMPROVEMENT";
export type ReplayCoachFeedbackReason = "CLEAR_NUMERICAL_EXPLANATION" | "CLEAR_CHART_REFERENCE" | "GOOD_PLAN_COMPARISON" | "EASY_TO_UNDERSTAND" | "ACTIONABLE_LESSON" | "CORRECT_CALCULATION" | "DID_NOT_ANSWER" | "TOO_GENERIC" | "MISSING_PRICES_OR_CALCULATIONS" | "MISSING_CHART_TIMES" | "INCORRECT_FACT_OR_CALCULATION" | "CONFUSED_EXECUTED_AND_SUGGESTED_PLAN" | "USED_FUTURE_INFORMATION" | "DIFFICULT_TO_UNDERSTAND" | "TOO_MUCH_INFORMATION" | "OTHER";
export type ReplayCoachFeedback = { id: number; assistant_message_id?: number; rating: ReplayCoachFeedbackRating; reason_code: ReplayCoachFeedbackReason | null; comment: string | null; created_at?: string; updated_at?: string };
export type ReplayCoachMessage = { id:number; analysis_id:number; sequence_number:number; role:ReplayCoachMessageRole; content:string; status:ReplayCoachMessageStatus; reply_to_message_id:number|null; inferred_intent:ReplayCoachFollowUpIntent|null; evidence_times:string[]; safe_error_code:string|null; created_at:string; completed_at:string|null; feedback:ReplayCoachFeedback|null };
export type ReplayCoachConversationResponse = { status:"success"; analysis_id:number; messages:ReplayCoachMessage[] };
export type ReplayCoachQuestionRequest = { question:string; client_request_id:string };
export type ReplayCoachQuestionResponse = { status:"success"; analysis_id:number; state:string; user_message:ReplayCoachMessage; assistant_message:ReplayCoachMessage|null; safe_error_code?:string };
export type ReplayCoachFeedbackRequest = { rating:ReplayCoachFeedbackRating; reason_code:ReplayCoachFeedbackReason|null; comment:string|null };
