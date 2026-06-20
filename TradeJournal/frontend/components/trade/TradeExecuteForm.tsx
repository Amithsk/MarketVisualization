//TradeJournal/frontend/components/trade/TradeExecuteForm.tsx

"use client"

import { useState } from "react"

type Props = {
  tradeDate: string

  onSubmit: (payload: {
    entry_timestamp?: string
  }) => Promise<void>

  onCancel?: () => void
}

export default function TradeExecuteForm({
  tradeDate,
  onSubmit,
  onCancel,
}: Props) {
  const [useCurrentTime, setUseCurrentTime] = useState(true)
  const [entryTime, setEntryTime] = useState("")
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    try {
      setLoading(true)

      if (useCurrentTime) {
        await onSubmit({})
        return
      }

      if (!entryTime) {
        alert("Please select an entry time")
        return
      }

      const entryTimestamp = `${tradeDate}T${entryTime}:00`

      await onSubmit({
        entry_timestamp: entryTimestamp,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-4 rounded-lg border bg-gray-50 p-4 space-y-4">
      <h3 className="text-sm font-semibold">Execute Trade</h3>

      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="radio"
            checked={useCurrentTime}
            onChange={() => setUseCurrentTime(true)}
          />
          Use Current Time
        </label>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="radio"
            checked={!useCurrentTime}
            onChange={() => setUseCurrentTime(false)}
          />
          Specify Entry Time
        </label>
      </div>

      {!useCurrentTime && (
        <div className="space-y-2">
          <label className="block text-sm font-medium">Entry Time</label>

          <input
            type="time"
            min="09:15"
            max="15:30"
            className="w-full rounded border px-3 py-2"
            value={entryTime}
            onChange={(e) => setEntryTime(e.target.value)}
          />

          {entryTime && (
            <div className="rounded border bg-white p-2 text-xs text-gray-600">
              Entry Timestamp:
              <br />
              {tradeDate} {entryTime}:00
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2">
        <button
          type="button"
          disabled={loading}
          onClick={submit}
          className="flex-1 rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Executing..." : "Confirm Execute"}
        </button>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded border px-3 py-2"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}
