import { useState } from "react"

import {
  createTradePlan,
  executeTrade,
  exitTrade,
  submitReview,
  fetchTradePlansByDate,
} from "@/services/tradeApi"

import {
  TradePlan,
  TradingDayState,
} from "@/types/trade"

// --------------------------------------------------
// Hook: useTradeActions
// --------------------------------------------------

export function useTradeActions(tradingDate: string) {
  const [plans, setPlans] = useState<TradePlan[]>([])
  const [dayState, setDayState] = useState<TradingDayState>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // --------------------------------------------------
  // Load all plans for the selected day
  // --------------------------------------------------
  const loadPlans = async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await fetchTradePlansByDate(tradingDate)

      setPlans(
        data.map((p: any) => ({
          id: p.id,
          plan_date: p.plan_date,
          strategy: p.strategy,
          position_type: p.position_type as "LONG" | "SHORT",
          plan_status: p.plan_status as "PLANNED" | "EXECUTED" | "NOT_TAKEN",
          trade_id: p.trade_id,
        }))
      )
    } catch (err: any) {
      setError(err.message || "Failed to load plans")
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Create trade plan
  // --------------------------------------------------
  const createPlan = async (payload: any) => {
    try {
      setLoading(true)
      setError(null)

      const res = await createTradePlan(payload)
      await loadPlans()

      setDayState({
        planId: res.plan_id,
        planStatus: "PLANNED",
        tradeExited: false,
        reviewCompleted: false,
      })
    } catch (err: any) {
      setError(err.message || "Failed to create plan")
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Execute trade
  // --------------------------------------------------
  const executePlan = async (planId: number) => {
    try {
      setLoading(true)
      setError(null)

      const res = await executeTrade(planId)
      await loadPlans()

      setDayState((prev) => ({
        ...prev,
        planId,
        tradeId: res.trade_id,
        planStatus: "EXECUTED",
      }))
    } catch (err: any) {
      setError(err.message || "Failed to execute trade")
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Exit trade
  // --------------------------------------------------
  const exitCurrentTrade = async (
    tradeId: number,
    payload: {
      exit_price: number
      exit_reason: string
      exit_timestamp: string
    }
  ) => {
    try {
      setLoading(true)
      setError(null)

      await exitTrade(tradeId, payload)

      setDayState((prev) => ({
        ...prev,
        tradeExited: true,
      }))
    } catch (err: any) {
      setError(err.message || "Failed to exit trade")
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Submit review
  // --------------------------------------------------
  const submitTradeReview = async (
    tradeId: number,
    payload: {
      exit_reason: string
      followed_entry_rules: boolean
      followed_stop_rules: boolean
      followed_position_sizing: boolean
      emotional_state: string
      market_context: string
      learning_insight: string
      trade_grade: string
    }
  ) => {
    try {
      setLoading(true)
      setError(null)

      await submitReview(tradeId, payload)

      setDayState((prev) => ({
        ...prev,
        reviewCompleted: true,
      }))
    } catch (err: any) {
      setError(err.message || "Failed to submit review")
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Select plan (multi-plan support)
  // --------------------------------------------------
  const selectPlan = (plan: TradePlan) => {
    setDayState({
      planId: plan.id,
      tradeId: plan.trade_id,
      planStatus: plan.plan_status,
      tradeExited: !!plan.trade_id,
      reviewCompleted: false,
    })
  }

  // --------------------------------------------------
  // Public API
  // --------------------------------------------------
  return {
    plans,
    dayState,
    loading,
    error,

    loadPlans,
    createPlan,
    executePlan,
    exitCurrentTrade,
    submitTradeReview,
    selectPlan,
  }
}
