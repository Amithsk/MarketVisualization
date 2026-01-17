type Props = {
  status: "NO_TRADES" | "PLANNED_ONLY" | "INCOMPLETE" | "COMPLETE"
}

export default function DayBadge({ status }: Props) {
  if (status === "NO_TRADES") return null

  const map = {
    PLANNED_ONLY: "🟦",
    INCOMPLETE: "⚠️",
    COMPLETE: "🟩",
  }

  return (
    <div className="absolute top-1 right-1 text-xs">
      {map[status]}
    </div>
  )
}
