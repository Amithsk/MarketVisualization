"use client"

type Props = {
  value: {
    exitPrice: string
    exitTimestamp: string
    exitReason: string
  }
  onChange: (v: Props["value"]) => void
  onSubmit: () => void
}

export default function TradeExitForm({
  value,
  onChange,
  onSubmit,
}: Props) {
  const update = (k: keyof Props["value"], v: string) => {
    onChange({ ...value, [k]: v })
  }

  const isValid =
    value.exitPrice &&
    value.exitTimestamp &&
    value.exitReason

  return (
    <div className="space-y-3 text-sm">
      <h3 className="font-semibold text-sm tracking-wide text-gray-700">
        2 · EXIT TRADE
      </h3>

      {/* Exit price */}
      <div>
        <label className="block font-medium">Exit Price *</label>
        <input
          className="w-full rounded-lg border p-2"
          value={value.exitPrice}
          onChange={(e) => update("exitPrice", e.target.value)}
          placeholder="e.g. 426.50"
        />
      </div>

      {/* Exit timestamp */}
      <div>
        <label className="block font-medium">Exit Time *</label>
        <input
          type="datetime-local"
          className="w-full rounded-lg border p-2"
          value={value.exitTimestamp}
          onChange={(e) => update("exitTimestamp", e.target.value)}
        />
      </div>

      {/* Exit reason */}
      <div>
        <label className="block font-medium">Exit Reason *</label>
        <select
          className="w-full rounded-lg border p-2"
          value={value.exitReason}
          onChange={(e) => update("exitReason", e.target.value)}
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
        onClick={onSubmit}
        className="w-full rounded-lg bg-black py-2 text-sm font-medium text-white hover:bg-gray-900 disabled:opacity-40"
      >
        ⏹ Confirm Exit
      </button>
    </div>
  )
}
