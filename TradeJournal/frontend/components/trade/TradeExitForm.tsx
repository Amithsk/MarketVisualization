"use client"

import { useEffect, useState } from "react"

type ExitPayload = {
  exit_price: number
  exit_timestamp: string
  exit_reason: string
  quantity?: number
  client_request_id?: string
}

type Props = {
  onSubmit: (payload: ExitPayload) => Promise<void>
  openQuantity?: number | null
  latestExecutionTimestamp?: string | null
}

export default function TradeExitForm({ onSubmit, openQuantity, latestExecutionTimestamp }: Props) {
  const [exitPrice, setExitPrice] = useState("")
  const [exitTimestamp, setExitTimestamp] = useState("")
  const [exitReason, setExitReason] = useState("")
  const [quantity, setQuantity] = useState(openQuantity?.toString() ?? "")
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  useEffect(() => setQuantity(openQuantity?.toString() ?? ""), [openQuantity])

  const isValid =
    exitPrice.trim() !== "" &&
    exitTimestamp.trim() !== "" &&
    exitReason.trim() !== ""

  const handleSubmit = async () => {
    if (!isValid) return
    setSubmitError(null)
    setSubmitting(true)
    try {
      const withSeconds = exitTimestamp.length === 16 ? `${exitTimestamp}:00` : exitTimestamp
      await onSubmit({ exit_price: Number(exitPrice), exit_timestamp: `${withSeconds}+05:30`,
        exit_reason: exitReason, quantity: quantity ? Number(quantity) : undefined,
        client_request_id: crypto.randomUUID() })
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Exit could not be saved")
    } finally { setSubmitting(false) }
  }

  return (
    <div className="space-y-3 text-sm">
      <h3 className="font-semibold tracking-wide text-gray-700">
        Exit Trade
      </h3>

      {/* Exit price */}
      {openQuantity !== undefined && <div><label className="block font-medium">Exit Quantity *</label><input type="number" min="1" max={openQuantity ?? undefined} className="w-full rounded border p-2" value={quantity} onChange={(e) => setQuantity(e.target.value)} /></div>}
      <div>
        <label className="block font-medium">Exit Price *</label>
        <input
          type="number"
          step="0.01"
          className="w-full rounded border p-2"
          value={exitPrice}
          onChange={(e) => setExitPrice(e.target.value)}
          placeholder="e.g. 590.00"
        />
      </div>

      {/* Exit timestamp */}
      <div>
        <label className="block font-medium">Exit Time *</label>
        <input
          type="datetime-local"
          step="1"
          min={latestExecutionTimestamp ? latestExecutionTimestamp.slice(0, 19) : undefined}
          className="w-full rounded border p-2"
          value={exitTimestamp}
          onChange={(e) => setExitTimestamp(e.target.value)}
        />
      </div>
      {submitError && <div role="alert" className="rounded border border-red-300 bg-red-50 p-2 text-red-700">{submitError}</div>}

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
        disabled={!isValid || submitting}
        onClick={handleSubmit}
        className="w-full rounded bg-black py-2 text-sm font-medium text-white hover:bg-gray-900 disabled:opacity-40"
      >
        ⏹ Confirm Exit
      </button>
    </div>
  )
}
