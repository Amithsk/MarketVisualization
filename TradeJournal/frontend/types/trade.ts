// ==============================
// ENUM TYPES (MATCH BACKEND)
// ==============================

export type PlanStatus = "PLANNED" | "EXECUTED" | "NOT_TAKEN"

export type PositionType = "LONG" | "SHORT"

export type TradeSide = "BUY" | "SELL"

export type TradeSource = "auto" | "manual" | "sim"

export type TradeStatus =
  | "sent"
  | "filled"
  | "partially_filled"
  | "cancelled"
  | "rejected"

// ==============================
// CORE DOMAIN MODELS
// ==============================

/**
 * TradePlan = planning-level entity
 * A trading day can have MULTIPLE plans
 */
export type TradePlan = {
  id: number

  // ✅ NEW — primary identity for the trade
  symbol: string

  plan_date: string

  strategy: string
  position_type: PositionType
  plan_status: PlanStatus

  trade_mode?: "PAPER" | "REAL"
  setup_description?: string
  entry_trigger?: string

  planned_entry_price?: number
  planned_stop_price?: number
  planned_target_price?: number
  planned_risk_amount?: number
  planned_position_size?: number

  not_taken_reason?: string | null

  // set ONLY after execution
  trade_id?: number | null
}

/**
 * TradeLog = execution-level entity
 * Created ONLY when a plan is executed
 */
export type TradeLog = {
  id: number
  timestamp: string

  // already exists and stays
  symbol: string

  side: TradeSide
  quantity: number
  price: number

  status: TradeStatus
  source: TradeSource

  entry_price?: number
  exit_price?: number
  exit_timestamp?: string
  exit_reason?: string

  pnl_amount?: number
  pnl_pct?: number
  trade_result?: "profit" | "loss" | "breakeven" | "open" | "cancelled"
}

/**
 * TradeExecutionReview = post-trade analysis
 */
export type TradeReview = {
  trade_id: number

  exit_reason:
    | "STOP_HIT"
    | "TARGET_HIT"
    | "TRAILING_STOP"
    | "MANUAL_FEAR"
    | "MANUAL_CONFUSION"
    | "RULE_VIOLATION"

  followed_entry_rules: boolean
  followed_stop_rules: boolean
  followed_position_sizing: boolean

  emotional_state:
    | "CALM"
    | "HESITANT"
    | "FEARFUL"
    | "CONFIDENT"
    | "FOMO"
    | "REVENGE"
    | "DISTRACTED"

  market_context:
    | "TRENDING"
    | "RANGE"
    | "CHOPPY"
    | "NEWS_DRIVEN"
    | "LOW_LIQUIDITY"

  learning_insight: string
  trade_grade: "A" | "B" | "C"
}

// ==============================
// UI / VIEW HELPERS
// ==============================

/**
 * Used ONLY for UI convenience
 * Derived from TradePlan + TradeLog
 */
export type TradePlanWithState = TradePlan & {
  isExecuted: boolean
  isExited: boolean
  isReviewed: boolean
}
