// frontend/types/calendar.ts

export type DayStatus = "COMPLETE" | "INCOMPLETE" | "NO_TRADES"

export type CalendarDay = {
  date: string        // YYYY-MM-DD
  day: number         // day number (1–31)
  isCurrentMonth: boolean
}



