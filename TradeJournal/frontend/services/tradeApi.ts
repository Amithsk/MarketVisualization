// frontend/lib/tradeApi.ts

const API_BASE = "http://localhost:8000/api";

/**
 * Low-level fetch wrapper
 */
async function api<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }

  return res.json();
}

/* =====================================================
   TRADE PLAN
===================================================== */

/**
 * Create a trade plan
 * POST /api/trade-plans
 */
export async function createTradePlan(payload: {
  plan_date: string;
  trade_mode: string;
  strategy: string;
  position_type: string;
  setup_description: string;
  planned_entry_price?: number;
  planned_stop_price?: number;
  planned_target_price?: number;
  planned_risk_amount?: number;
  planned_position_size: number;
}) {
  return api<{ plan_id: number }>("/trade-plans", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Fetch all trade plans for a date
 * GET /api/trade-plans?date=YYYY-MM-DD
 */
export async function fetchTradePlansByDate(date: string) {
  return api<
    Array<{
      id: number;
      plan_date: string;
      strategy: string;
      position_type: string;
      plan_status: string;
      trade_id?: number;
    }>
  >(`/trade-plans?date=${date}`);
}

/* =====================================================
   EXECUTION
===================================================== */

/**
 * Execute a trade plan
 * POST /api/trade-plans/{plan_id}/execute
 */
export async function executeTrade(planId: number) {
  return api<{ trade_id: number; status: string }>(
    `/trade-plans/${planId}/execute`,
    { method: "POST" }
  );
}

/**
 * Exit a trade
 * POST /api/trades/{trade_id}/exit
 */
export async function exitTrade(
  tradeId: number,
  payload: {
    exit_price: number;
    exit_reason: string;
    exit_timestamp: string;
  }
) {
  return api<{ status: string }>(`/trades/${tradeId}/exit`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/* =====================================================
   REVIEW
===================================================== */

/**
 * Submit post-trade review
 * POST /api/trades/{trade_id}/review
 */
export async function submitReview(
  tradeId: number,
  payload: {
    exit_reason: string;
    followed_entry_rules: boolean;
    followed_stop_rules: boolean;
    followed_position_sizing: boolean;
    emotional_state: string;
    market_context: string;
    learning_insight: string;
    trade_grade: string;
  }
) {
  return api<{ status: string }>(`/trades/${tradeId}/review`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
