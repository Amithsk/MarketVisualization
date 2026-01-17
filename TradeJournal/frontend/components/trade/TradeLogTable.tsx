"use client"

import { useState } from "react"

type ExitPayload = {
  exit_price: number
  exit_timestamp: string
  exit_reason: string
}

type Props = {
  tradeExited: boolean
  onExit: (payload: ExitPayload) => Promise<void>
}

const EXIT_REASONS = [
  { value: "STOP_HIT", label: "Stop Hit" },
  { value: "TARGET_HIT", label: "Target Hit" },
  { value: "TRAILING_STOP", label: "Trailing Stop" },
  { value: "MANUAL_FEAR", label: "Manual (Fear)" },
  { value: "MANUAL_CONFUSION", label: "Manual (Confusion)" },
  { value: "RULE_VIOLATION", label: "Rule Violation" },
]

export default function TradeLogTable({ tradeExited, onExit }: Props) {
  const [exitPrice, setExitPrice] = useState("")
  const [exitTimestamp, setExitTimestamp] = useState("")
  const [exitReason, setExitReason] = useState("")

  if (tradeExited) {
    return (
      <div className="mt-4 rounded bg-gray-100 p-3 text-sm">
        Trade exited
      </div>
    )
  }

  const submit = async () => {
    await onExit({
      exit_price: Number(exitPrice),
      exit_timestamp: exitTimestamp,
      exit_reason: exitReason,
    })
  }

  return (
    <div className="mt-4 space-y-3">
      <h3 className="text-sm font-semibold">Exit Trade</h3>

      <input
        className="w-full rounded border px-2 py-1"
        placeholder="Exit price"
        value={exitPrice}
        onChange={(e) => setExitPrice(e.target.value)}
      />

      <input
        type="datetime-local"
        className="w-full rounded border px-2 py-1"
        value={exitTimestamp}
        onChange={(e) => setExitTimestamp(e.target.value)}
      />

      <select
        className="w-full rounded border px-2 py-1"
        value={exitReason}
        onChange={(e) => setExitReason(e.target.value)}
      >
        <option value="">Select exit reason</option>
        {EXIT_REASONS.map((r) => (
          <option key={r.value} value={r.value}>
            {r.label}
          </option>
        ))}
      </select>

      <button
        className="w-full rounded bg-red-600 px-3 py-2 text-white"
        onClick={submit}
      >
        Exit Trade
      </button>
    </div>
  )
}
