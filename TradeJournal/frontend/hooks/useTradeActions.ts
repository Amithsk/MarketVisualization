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
    await createTradePlan({
      ...payload,
      plan_date: tradingDate,
    })

    await loadPlans()
  }

  /* ---------------- EXECUTE PLAN ---------------- */

  const executePlan = async (planId: number) => {
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
    await exitTrade(tradeId, payload)
    await loadPlans()
  }

  /* ---------------- REVIEW ---------------- */

  const submitReview = async (tradeId: number, payload: any) => {
    await submitTradeReview(tradeId, payload)
    await loadPlans()
  }

  /* ---------------- DERIVED UI RULES ---------------- */

  const executedPlans = plans.filter(
    (p) => p.plan_status === "EXECUTED"
  )

  const canExecuteMoreTrades = true
  // intentionally flexible — can later enforce:
  // - max concurrent trades
  // - strategy caps
  // - risk rules
  // - market condition rules

  /* ---------------- PUBLIC API ---------------- */

  return {
    /* data */
    plans,

    /* derived info (read-only) */
    executedPlans,
    canExecuteMoreTrades,

    /* flags */
    loading,
    error,

    /* actions */
    loadPlans,
    createPlan,
    executePlan,
    exitTrade: exitTradeAction,
    submitTradeReview: submitReview,
  }
}
