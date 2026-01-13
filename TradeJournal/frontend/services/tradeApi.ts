// frontend/services/tradeApi.ts

const API_BASE = "http://localhost:8000/api"

/* -----------------------------
   TYPES
----------------------------- */

export type CreatePlanResponse = {
  plan_id: number
}

/* -----------------------------
   API HELPER
----------------------------- */

async function api(url: string, options: RequestInit = {}) {
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }

  return res.json()
}

/* -----------------------------
   TRADE PLAN
----------------------------- */

export async function createTradePlan(
  payload: any
): Promise<CreatePlanResponse> {
  return api(`${API_BASE}/trade-plans`, {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

/* -----------------------------
   EXECUTE
----------------------------- */

export async function executeTrade(planId: number) {
  return api(`${API_BASE}/trade-plans/${planId}/execute`, {
    method: "POST",
  })
}

/* -----------------------------
   EXIT
----------------------------- */

export async function exitTrade(tradeId: number, payload: any) {
  return api(`${API_BASE}/trades/${tradeId}/exit`, {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

/* -----------------------------
   REVIEW
----------------------------- */

export async function submitReview(tradeId: number, payload: any) {
  return api(`${API_BASE}/trades/${tradeId}/review`, {
    method: "POST",
    body: JSON.stringify(payload),
  })
}
