"use client"

import clsx from "clsx"
import { CalendarDay } from "@/types/calendar"

type Props = {
  day: CalendarDay
  onClick: () => void
}

export default function CalendarCell({ day, onClick }: Props) {
  const tradeCount = day.tradeCount
  const pnl = day.pnl

  const isCurrent = day.isCurrentMonth
  const hasTrades = tradeCount > 0

  return (
    <button
      onClick={onClick}
      className={clsx(
        "h-24 w-full rounded-xl border bg-white p-2 text-sm",
        "flex flex-col justify-between",
        "transition-all hover:bg-gray-50 hover:shadow-sm",
        !isCurrent && "bg-gray-50 text-gray-400 hover:bg-gray-50"
      )}
    >
      {/* ───── TOP: Trade Count ───── */}
      <div className="text-[11px] font-medium text-gray-500">
        {hasTrades ? `${tradeCount}T` : ""}
      </div>

      {/* ───── CENTER: Date ───── */}
      <div className="flex justify-center">
        <span
          className={clsx(
            "text-lg font-semibold",
            !isCurrent && "text-gray-400"
          )}
        >
          {day.day}
        </span>
      </div>

      {/* ───── BOTTOM: P&L ───── */}
      <div
        className={clsx(
          "text-[11px] font-semibold text-center",
          !isCurrent && "text-transparent",
          isCurrent &&
            (pnl > 0
              ? "text-green-600"
              : pnl < 0
              ? "text-red-600"
              : "text-gray-500")
        )}
      >
        {isCurrent
          ? pnl > 0
            ? `+₹${pnl.toLocaleString()}`
            : pnl < 0
            ? `-₹${Math.abs(pnl).toLocaleString()}`
            : "₹0"
          : "—"}
      </div>
    </button>
  )
}
