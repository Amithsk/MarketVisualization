// frontend/types/calendar.ts

export type DayStatus = "COMPLETE" | "INCOMPLETE" | "NO_TRADES"

export type CalendarDay = {
  date: string        // YYYY-MM-DD
  day: number         // day number (1–31)
  isCurrentMonth: boolean

  // ------------------------------
  // UI-only calendar enhancements
  // ------------------------------
  tradeCount: number  // ALWAYS present (0 if no trades)
  pnl: number         // ALWAYS present (0 if breakeven / no trades)
}
