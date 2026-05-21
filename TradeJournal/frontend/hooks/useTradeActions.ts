//TradeJournal/frontend/hooks/useTradeActions.ts
"use client"

import { useCallback, useEffect, useState } from "react"

import {
  fetchTradePlansByDate,
  createTradePlan,
  executeTradePlan,
  exitTrade,
  submitTradeReview,
} from "@/services/tradeApi"

import { TradePlan } from "@/types/trade"

/* ======================================================
   Hook — Plan-centric, Multi-plan safe
====================================================== */

export function useTradeActions(tradingDate: string) {
  /* ---------------- STATE ---------------- */

  const [plans, setPlans] = useState<TradePlan[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /* ---------------- LOAD PLANS ---------------- */

  const loadPlans = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await fetchTradePlansByDate(tradingDate)
      setPlans(data)
    } catch (err) {
      console.error("❌ loadPlans error:", err)
      setError("Failed to load trade plans")
    } finally {
      setLoading(false)
    }
  }, [tradingDate])

  useEffect(() => {
    loadPlans()
  }, [loadPlans])

  /* ---------------- CREATE PLAN ---------------- */

  const createPlan = async (payload: any) => {
    console.group("🟢 useTradeActions.createPlan")
    console.log("Incoming payload:", payload)
    console.groupEnd()

    await createTradePlan({
      ...payload,
      plan_date: tradingDate,
    })

    await loadPlans()
  }

  /* ---------------- EXECUTE PLAN ---------------- */

  const executePlan = async (planId: number) => {
    console.group("🟢 useTradeActions.executePlan")
    console.log("planId:", planId)
    console.groupEnd()

    await executeTradePlan(planId)
    await loadPlans()
  }

  /* ---------------- EXIT TRADE ---------------- */

  const exitTradeAction = async (
    tradeId: number,
    payload: {
      exit_price: number
      exit_reason: string
      exit_timestamp: string
    }
  ) => {
    console.group("🔴 useTradeActions.exitTradeAction")
    console.log("tradeId:", tradeId)
    console.log("payload RECEIVED:", payload)
    console.log("payload JSON:", JSON.stringify(payload))
    console.groupEnd()

    await exitTrade(tradeId, payload)

    console.log("✅ exitTrade API call completed")

    await loadPlans()
  }

  /* ---------------- REVIEW ---------------- */

  const submitReview = async (tradeId: number, payload: any) => {
    console.group("🟣 useTradeActions.submitReview")
    console.log("tradeId:", tradeId)
    console.log("payload:", payload)
    console.groupEnd()

    await submitTradeReview(tradeId, payload)
    await loadPlans()
  }

  /* ---------------- DERIVED UI RULES ---------------- */

   
  const plannedTrades = plans.filter((p) =>!p.trade_state?.is_executed && p.plan_status === "PLANNED")

  const activeTrades = plans.filter((p) =>p.trade_state?.is_executed &&!p.trade_state?.is_exited)

  const pendingReviews = plans.filter((p) =>p.trade_state?.is_exited &&!p.trade_state?.is_reviewed)

  const completedTrades = plans.filter((p) => p.trade_state?.is_reviewed)

  const canExecuteMoreTrades = true

  /* ---------------- PUBLIC API ---------------- */

  return {
    plans,

    plannedTrades,
    activeTrades,
    pendingReviews,
    completedTrades,
    canExecuteMoreTrades,

    loading,
    error,

    loadPlans,
    createPlan,
    executePlan,
    exitTrade: exitTradeAction,
    submitTradeReview: submitReview,
  }
}
