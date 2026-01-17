"use client"

import { useState } from "react"
import { CalendarDay } from "@/types/calendar"

function formatDate(date: Date) {
  return date.toISOString().split("T")[0]
}

export function useCalendar() {
  const [current, setCurrent] = useState(() => {
    const d = new Date()
    d.setDate(1)
    return d
  })

  const year = current.getFullYear()
  const month = current.getMonth()

  const startOfMonth = new Date(year, month, 1)
  const endOfMonth = new Date(year, month + 1, 0)

  const startDay = startOfMonth.getDay() // Sun = 0
  const totalDays = endOfMonth.getDate()

  const days: CalendarDay[] = []

  // ---- Previous month filler ----
  for (let i = startDay - 1; i >= 0; i--) {
    const d = new Date(year, month, -i)
    days.push({
      date: formatDate(d),
      day: d.getDate(),
      isCurrentMonth: false,
    })
  }

  // ---- Current month ----
  for (let day = 1; day <= totalDays; day++) {
    const d = new Date(year, month, day)
    days.push({
      date: formatDate(d),
      day,
      isCurrentMonth: true,
    })
  }

  // ---- Next month filler (to complete grid) ----
  while (days.length % 7 !== 0) {
    const last = days[days.length - 1]
    const d = new Date(last.date)
    d.setDate(d.getDate() + 1)

    days.push({
      date: formatDate(d),
      day: d.getDate(),
      isCurrentMonth: false,
    })
  }

  const goPrev = () => {
    setCurrent(new Date(year, month - 1, 1))
  }

  const goNext = () => {
    setCurrent(new Date(year, month + 1, 1))
  }

  const goToday = () => {
    const d = new Date()
    d.setDate(1)
    setCurrent(d)
  }

  const monthLabel = current.toLocaleString("default", {
    month: "long",
    year: "numeric",
  })

  return {
    currentMonth: monthLabel,
    days,
    goPrev,
    goNext,
    goToday,
  }
}
