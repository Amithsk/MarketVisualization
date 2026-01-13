"use client"

import { useState } from "react"

export type TradePlanPayload = {
  plan_date: string
  trade_mode: "PAPER" | "REAL"
  strategy: string
  position_type: "LONG" | "SHORT"
  setup_description: string
  planned_entry_price?: number
  planned_stop_price?: number
  planned_target_price?: number
  planned_risk_amount: number
  planned_position_size: number
}

type Props = {
  tradeDate: string
  onSubmit: (payload: TradePlanPayload) => Promise<void>
}

export default function TradePlanForm({ tradeDate, onSubmit }: Props) {
  const [form, setForm] = useState<TradePlanPayload>({
    plan_date: tradeDate,
    trade_mode: "PAPER",          // ✅ DEFAULT
    strategy: "",
    position_type: "LONG",
    setup_description: "",
    planned_risk_amount: 0,
    planned_position_size: 0,
  })

  const update = (k: keyof TradePlanPayload, v: any) =>
    setForm((f) => ({ ...f, [k]: v }))

  return (
    <div className="space-y-2">
      <h3 className="font-semibold">Trade Plan</h3>

      {/* ✅ TRADE MODE */}
      <label className="block text-sm">Trade Mode</label>
      <select
        value={form.trade_mode}
        onChange={(e) => update("trade_mode", e.target.value)}
        className="w-full border px-2 py-1"
      >
        <option value="PAPER">PAPER</option>
        <option value="REAL">REAL</option>
      </select>

      {/* STRATEGY */}
      <select
        value={form.strategy}
        onChange={(e) => update("strategy", e.target.value)}
        className="w-full border px-2 py-1"
      >
        <option value="">Select Strategy</option>
        <option value="ORB">ORB</option>
        <option value="BREAKOUT">Breakout</option>
        <option value="PULLBACK">Pullback</option>
      </select>

      {/* DIRECTION */}
      <select
        value={form.position_type}
        onChange={(e) => update("position_type", e.target.value)}
        className="w-full border px-2 py-1"
      >
        <option value="LONG">LONG</option>
        <option value="SHORT">SHORT</option>
      </select>

      <textarea
        placeholder="Setup description"
        className="w-full border p-2"
        value={form.setup_description}
        onChange={(e) => update("setup_description", e.target.value)}
      />

      <input
        placeholder="Planned Entry Price (optional)"
        type="number"
        className="w-full border px-2 py-1"
        onChange={(e) => update("planned_entry_price", Number(e.target.value))}
      />

      <input
        placeholder="Planned Stop Price (optional)"
        type="number"
        className="w-full border px-2 py-1"
        onChange={(e) => update("planned_stop_price", Number(e.target.value))}
      />

      <input
        placeholder="Planned Target Price (optional)"
        type="number"
        className="w-full border px-2 py-1"
        onChange={(e) =>
          update("planned_target_price", Number(e.target.value))
        }
      />

      <input
        placeholder="Planned Risk Amount"
        type="number"
        className="w-full border px-2 py-1"
        onChange={(e) =>
          update("planned_risk_amount", Number(e.target.value))
        }
      />

      <input
        placeholder="Planned Position Size"
        type="number"
        className="w-full border px-2 py-1"
        onChange={(e) =>
          update("planned_position_size", Number(e.target.value))
        }
      />

      <button
        className="w-full border bg-gray-100 py-1 hover:bg-gray-200"
        onClick={() => onSubmit(form)}
      >
        Save Trade Plan
      </button>
    </div>
  )
}
