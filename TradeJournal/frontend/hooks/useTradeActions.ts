"use client"

import { useState } from "react"
import {
  createTradePlan,
  executeTrade,
  exitTrade,
  submitReview,
} from "@/services/tradeApi"

/* -----------------------------
   TYPES
----------------------------- */

export type TradePlanPayload = {
  plan_date: string
  trade_mode: "PAPER" | "REAL"
  strategy: string
  position_type: "LONG" | "SHORT"
  setup_description: string
  planned_entry_price?: number
  planned_stop_price?: number
  planned_target_price?: number
  planned_risk_amount: number
  planned_position_size: number
}

export type TradingDayState = {
  planId?: number
  tradeId?: number
  planStatus?: "PLANNED" | "EXECUTED"
  tradeExited?: boolean
  reviewCompleted?: boolean
}

/* -----------------------------
   HOOK
----------------------------- */

export function useTradeActions() {
  const [state, setState] = useState<TradingDayState | null>(null)
  const [loading, setLoading] = useState(false)

  /* ---------- PLAN ---------- */
  const createPlan = async (payload: TradePlanPayload) => {
    console.log("🟡 createPlan called with payload:", payload)

    setLoading(true)
    try {
      // ✅ FIX: backend returns { plan_id }, NOT { id }
      const res = await createTradePlan(payload)

      console.log("🟢 createTradePlan response:", res)

      setState({
        planId: res.plan_id,
        planStatus: "PLANNED",
        tradeExited: false,
        reviewCompleted: false,
      })

      console.log("🟢 state AFTER createPlan:", {
        planId: res.plan_id,
        planStatus: "PLANNED",
      })
    } finally {
      setLoading(false)
    }
  }

  /* ---------- EXECUTE ---------- */
  const execute = async () => {
    console.log("🟡 execute clicked, current state:", state)

    if (!state?.planId) {
      console.error("🔴 planId missing at execute time")
      throw new Error("planId missing")
    }

    setLoading(true)
    try {
      const res: { trade_id: number } = await executeTrade(state.planId)

      console.log("🟢 executeTrade response:", res)

      setState((prev) => ({
        ...prev!,
        tradeId: res.trade_id,
        planStatus: "EXECUTED",
      }))
    } finally {
      setLoading(false)
    }
  }

  /* ---------- EXIT ---------- */
  const exit = async (payload: {
    exit_price: number
    exit_timestamp: string
    exit_reason: string
  }) => {
    console.log("🟡 exit called, payload:", payload)
    console.log("🟡 current state:", state)

    if (!state?.tradeId) {
      throw new Error("tradeId missing")
    }

    setLoading(true)
    try {
      await exitTrade(state.tradeId, payload)

      setState((prev) => ({
        ...prev!,
        tradeExited: true,
      }))
    } finally {
      setLoading(false)
    }
  }

  /* ---------- REVIEW ---------- */
  const review = async (payload: {
    followed_entry_rules: boolean
    followed_stop_rules: boolean
    followed_position_sizing: boolean
    emotional_state: string
    market_context: string
    learning_insight: string
    trade_grade: "A" | "B" | "C"
  }) => {
    console.log("🟡 review called, payload:", payload)
    console.log("🟡 current state:", state)

    if (!state?.tradeId) {
      throw new Error("tradeId missing")
    }

    setLoading(true)
    try {
      await submitReview(state.tradeId, payload)

      setState((prev) => ({
        ...prev!,
        reviewCompleted: true,
      }))
    } finally {
      setLoading(false)
    }
  }

  return {
    state,
    loading,
    createPlan,
    execute,
    exit,
    review,
  }
}
