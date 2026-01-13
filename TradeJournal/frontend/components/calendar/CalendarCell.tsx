"use client"

import clsx from "clsx"
import { CalendarDay } from "@/types/calendar"

type Props = {
  day: CalendarDay
  onClick: () => void
}

export default function CalendarCell({ day, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "h-20 w-full rounded border p-1 text-left text-sm hover:bg-gray-100",
        !day.isCurrentMonth && "bg-gray-50 text-gray-400"
      )}
    >
      <div className="font-medium">{day.day}</div>
    </button>
  )
}
