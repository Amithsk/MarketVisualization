export type TradingDayState = {
  planId?: number
  tradeId?: number
  planStatus?: "PLANNED" | "EXECUTED" | "NOT_TAKEN"
  tradeExited?: boolean
  reviewCompleted?: boolean
}
