// frontend/hooks/useTradeDrawer.ts
"use client"

import { useState } from "react"

export function useTradeDrawer() {
  const [open, setOpen] = useState(false)
  const [date, setDate] = useState<string | null>(null)

  return {
    open,
    date,
    openForDate: (d: string) => {
      setDate(d)
      setOpen(true)
    },
    close: () => setOpen(false),
  }
}
