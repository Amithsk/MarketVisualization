// frontend/components/calendar/WeekdayHeader.tsx
export default function WeekdayHeader() {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  return (
    <div className="grid grid-cols-7 mb-2 text-sm font-medium text-gray-600">
      {days.map((d) => (
        <div key={d} className="text-center">
          {d}
        </div>
      ))}
    </div>
  )
}
