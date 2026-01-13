"use client"

type TradePlanDraft = {
  strategy: string
  direction: "LONG" | "SHORT"
  setup: string
  entry: string
  stop: string
  target: string
  risk: string
}

type Props = {
  value: TradePlanDraft
  onChange: (next: TradePlanDraft) => void
}

export default function TradePlanCard({ value, onChange }: Props) {
  const update = <K extends keyof TradePlanDraft>(
    key: K,
    val: TradePlanDraft[K]
  ) => {
    onChange({ ...value, [key]: val })
  }

  return (
    <div className="space-y-3 rounded border p-4">
      <h3 className="font-semibold">Trade Plan</h3>

      <input
        className="w-full border p-2"
        placeholder="Strategy"
        value={value.strategy}
        onChange={(e) => update("strategy", e.target.value)}
      />

      <select
        className="w-full border p-2"
        value={value.direction}
        onChange={(e) =>
          update("direction", e.target.value as "LONG" | "SHORT")
        }
      >
        <option value="LONG">Long</option>
        <option value="SHORT">Short</option>
      </select>

      <textarea
        className="w-full border p-2"
        placeholder="Setup description"
        value={value.setup}
        onChange={(e) => update("setup", e.target.value)}
      />

      <input
        className="w-full border p-2"
        placeholder="Planned entry"
        value={value.entry}
        onChange={(e) => update("entry", e.target.value)}
      />

      <input
        className="w-full border p-2"
        placeholder="Planned stop"
        value={value.stop}
        onChange={(e) => update("stop", e.target.value)}
      />

      <input
        className="w-full border p-2"
        placeholder="Target (optional)"
        value={value.target}
        onChange={(e) => update("target", e.target.value)}
      />

      <input
        className="w-full border p-2"
        placeholder="Risk (₹)"
        value={value.risk}
        onChange={(e) => update("risk", e.target.value)}
      />
    </div>
  )
}
