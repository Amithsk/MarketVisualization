// frontend/services/calendarApi.ts

const API_BASE = "http://localhost:8000/api"

/**
 * Backend response shape for calendar aggregation
 * Example:
 * {
 *   "2026-01-14": { tradeCount: 2, pnl: 1500 },
 *   "2026-01-15": { tradeCount: 1, pnl: -300 }
 * }
 */
export type CalendarSummaryResponse = Record<
  string,
  {
    tradeCount: number
    pnl: number
  }
>

/**
 * Fetch aggregated trade summary for a month
 */
export async function fetchCalendarSummary(
  year: number,
  month: number // 1–12
): Promise<CalendarSummaryResponse> {
  const res = await fetch(
    `${API_BASE}/calendar/summary?year=${year}&month=${month}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || "Failed to fetch calendar summary")
  }

  return res.json()
}
