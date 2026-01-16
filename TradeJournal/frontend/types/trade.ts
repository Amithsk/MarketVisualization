// --------------------------------------------------
// Trading day UI state (USED BY DRAWER / STEPPER)
// --------------------------------------------------
export type TradingDayState = {
  planId?: number
  tradeId?: number
  planStatus?: "PLANNED" | "EXECUTED" | "NOT_TAKEN"
  tradeExited?: boolean
  reviewCompleted?: boolean
}

// --------------------------------------------------
// DOMAIN TYPES (API + BUSINESS LOGIC)
// --------------------------------------------------

export type PositionType = "LONG" | "SHORT"

export type PlanStatus = "PLANNED" | "EXECUTED" | "NOT_TAKEN"

// Single trade plan (backend: trade_plan)
export type TradePlan = {
  id: number
  plan_date: string
  strategy: string
  position_type: PositionType
  plan_status: PlanStatus
  trade_id?: number
}

// (Optional – will be used in Phase 3 summary)
export type TradeSummary = {
  totalTrades: number
  wins: number
  losses: number
  winRate: number
  totalPnL: number
}
