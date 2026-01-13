"use client"

import { useState } from "react"

import CalendarHeader from "@/components/calendar/CalendarHeader"
import CalendarGrid from "@/components/calendar/CalendarGrid"
import CalendarCell from "@/components/calendar/CalendarCell"
import WeekdayHeader from "@/components/calendar/WeekdayHeader"
import TradeDrawer from "@/components/trade/TradeDrawer"

import { useCalendar } from "@/hooks/useCalendar"

export default function CalendarPage() {
  const { currentMonth, days, goPrev, goNext, goToday } = useCalendar()

  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  return (
    <div className="p-6">
      <CalendarHeader
        month={currentMonth}
        onPrev={goPrev}
        onNext={goNext}
        onToday={goToday}
      />

      <WeekdayHeader />

      <CalendarGrid>
        {days.map((d) => (
          <CalendarCell
            key={d.date}
            day={d}
            onClick={() => setSelectedDate(d.date)}
          />
        ))}
      </CalendarGrid>

      {selectedDate && (
        <TradeDrawer
          tradeDate={selectedDate}
          onClose={() => setSelectedDate(null)}
        />
      )}
    </div>
  )
}
