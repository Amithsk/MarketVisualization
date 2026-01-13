"use client"

type Props = {
  month: string
  onPrev: () => void
  onNext: () => void
  onToday: () => void
}

export default function CalendarHeader({
  month,
  onPrev,
  onNext,
  onToday,
}: Props) {
  return (
    <div className="mb-4 flex items-center justify-between">
      <div className="flex gap-2">
        <button
          className="rounded border px-2 py-1 text-sm"
          onClick={onPrev}
        >
          ←
        </button>
        <button
          className="rounded border px-2 py-1 text-sm"
          onClick={onNext}
        >
          →
        </button>
        <button
          className="rounded border px-2 py-1 text-sm"
          onClick={onToday}
        >
          Today
        </button>
      </div>

      <div className="text-lg font-semibold">{month}</div>
    </div>
  )
}
