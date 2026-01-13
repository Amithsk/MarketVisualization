// frontend/components/calendar/CalendarGrid.tsx
import { ReactNode } from "react"

export default function CalendarGrid({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-7 gap-2">
      {children}
    </div>
  )
}
