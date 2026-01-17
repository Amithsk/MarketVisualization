import { TradePlan, TradeReview } from "@/types/trade"

const API_BASE = "http://localhost:8000/api"

/* ===============================
   LOW-LEVEL FETCH WRAPPER
   (FIXED – DO NOT CHANGE)
================================ */

async function api<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || "API request failed")
  }

  return res.json()
}

/* ===============================
   TRADE PLANS
================================ */

/**
 * Fetch all trade plans for a specific trading date
 */
export async function fetchTradePlansByDate(
  tradeDate: string
): Promise<TradePlan[]> {
  return api<TradePlan[]>(
    `/trade-plans?trade_date=${tradeDate}`
  )
}

/**
 * Create a new trade plan
 */
export async function createTradePlan(
  payload: Partial<TradePlan>
): Promise<{ plan_id: number }> {
  return api<{ plan_id: number }>(`/trade-plans`, {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

/**
 * Execute a trade plan (creates TradeLog in backend)
 */
export async function executeTradePlan(
  planId: number
): Promise<{ trade_id: number; status: "EXECUTED" }> {
  return api<{ trade_id: number; status: "EXECUTED" }>(
    `/trade-plans/${planId}/execute`,
    { method: "POST" }
  )
}

/* ===============================
   TRADE EXECUTION
================================ */

/**
 * Exit an executed trade
 */
export async function exitTrade(
  tradeId: number,
  payload: {
    exit_price: number
    exit_reason: string
    exit_timestamp: string
  }
): Promise<{ status: "EXITED" }> {
  return api<{ status: "EXITED" }>(
    `/trades/${tradeId}/exit`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  )
}

/**
 * Submit post-trade review
 */
export async function submitTradeReview(
  tradeId: number,
  payload: Omit<TradeReview, "trade_id">
): Promise<{ status: "REVIEWED" }> {
  return api<{ status: "REVIEWED" }>(
    `/trades/${tradeId}/review`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  )
}
