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
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto p-6 space-y-6">

        {/* ============================= */}
        {/* CALENDAR HEADER */}
        {/* ============================= */}
        <div className="bg-white rounded-xl border shadow-sm p-4">
          <CalendarHeader
            month={currentMonth}
            onPrev={goPrev}
            onNext={goNext}
            onToday={goToday}
          />
        </div>

        {/* ============================= */}
        {/* WEEK / MONTH GRID */}
        {/* ============================= */}
        <div className="bg-white rounded-xl border shadow-sm p-4 space-y-4">

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

        </div>

        {/* ============================= */}
        {/* TRADE JOURNAL DRAWER */}
        {/* ============================= */}
        {selectedDate && (
          <div className="bg-white rounded-xl border shadow-sm overflow-hidden">

            <TradeDrawer
              tradeDate={selectedDate}
              onClose={() => setSelectedDate(null)}
            />

          </div>
        )}

      </div>
    </div>
  )
}

