"use client"

import { useState } from "react"

type ExitPayload = {
  exit_price: number
  exit_timestamp: string
  exit_reason: string
}

type Props = {
  onSubmit: (payload: ExitPayload) => void
}

export default function TradeExitForm({ onSubmit }: Props) {
  const [exitPrice, setExitPrice] = useState("")
  const [exitTimestamp, setExitTimestamp] = useState("")
  const [exitReason, setExitReason] = useState("")

  const isValid =
    exitPrice !== "" &&
    exitTimestamp !== "" &&
    exitReason !== ""

  const handleSubmit = () => {
    if (!isValid) return

    onSubmit({
      exit_price: Number(exitPrice),
      exit_timestamp: exitTimestamp,
      exit_reason: exitReason,
    })
  }

  return (
    <div className="space-y-3 text-sm">
      <h3 className="font-semibold tracking-wide text-gray-700">
        Exit Trade
      </h3>

      {/* Exit price */}
      <div>
        <label className="block font-medium">Exit Price *</label>
        <input
          className="w-full rounded border p-2"
          value={exitPrice}
          onChange={(e) => setExitPrice(e.target.value)}
          placeholder="e.g. 426.50"
        />
      </div>

      {/* Exit timestamp */}
      <div>
        <label className="block font-medium">Exit Time *</label>
        <input
          type="datetime-local"
          className="w-full rounded border p-2"
          value={exitTimestamp}
          onChange={(e) => setExitTimestamp(e.target.value)}
        />
      </div>

      {/* Exit reason */}
      <div>
        <label className="block font-medium">Exit Reason *</label>
        <select
          className="w-full rounded border p-2"
          value={exitReason}
          onChange={(e) => setExitReason(e.target.value)}
        >
          <option value="">Select reason</option>
          <option value="TARGET_HIT">Target Hit</option>
          <option value="STOP_HIT">Stop Hit</option>
          <option value="TRAILING_STOP">Trailing Stop</option>
          <option value="MANUAL_FEAR">Manual – Fear</option>
          <option value="MANUAL_CONFUSION">Manual – Confusion</option>
          <option value="RULE_VIOLATION">Rule Violation</option>
        </select>
      </div>

      <button
        disabled={!isValid}
        onClick={handleSubmit}
        className="w-full rounded bg-black py-2 text-sm font-medium text-white hover:bg-gray-900 disabled:opacity-40"
      >
        ⏹ Confirm Exit
      </button>
    </div>
  )
}
