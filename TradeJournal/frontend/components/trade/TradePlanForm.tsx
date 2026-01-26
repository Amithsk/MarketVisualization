"use client"

import { useState } from "react"

type Props = {
  onSubmit: (data: any) => void
}

/**
 * UI-only strategy list
 */
const STRATEGIES = [
  "ORB",
  "VWAP",
  "GAP",
  "BREAKOUT",
  "REVERSAL",
]

export default function TradePlanForm({ onSubmit }: Props) {
  const [form, setForm] = useState({
    symbol: "",
    plan_date: "",
    trade_mode: "PAPER",
    strategy: "",
    position_type: "LONG",
    setup_description: "",
    planned_entry_price: "",
    planned_stop_price: "",
    planned_target_price: "",
    planned_risk_amount: "",
    planned_position_size: "",
  })

  const update = (k: keyof typeof form, v: string) => {
    setForm((prev) => ({ ...prev, [k]: v }))
  }

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-sm border p-6 space-y-6">
      <h2 className="text-xl font-semibold text-gray-800">
        Create Trade Plan
      </h2>

      {/* SYMBOL */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Symbol *
        </label>
        <input
          placeholder="e.g. RELIANCE, NIFTY, BANKNIFTY"
          className="w-full border rounded-md px-3 py-2"
          value={form.symbol}
          onChange={(e) =>
            update("symbol", e.target.value.toUpperCase())
          }
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <input
          type="date"
          className="border rounded-md px-3 py-2"
          value={form.plan_date}
          onChange={(e) =>
            update("plan_date", e.target.value)
          }
        />

        <select
          className="border rounded-md px-3 py-2"
          value={form.trade_mode}
          onChange={(e) =>
            update("trade_mode", e.target.value)
          }
        >
          <option value="PAPER">Paper</option>
          <option value="REAL">Real</option>
        </select>

        {/* STRATEGY */}
        <select
          className="border rounded-md px-3 py-2 col-span-2"
          value={form.strategy}
          onChange={(e) =>
            update("strategy", e.target.value)
          }
        >
          <option value="">Select Strategy</option>
          {STRATEGIES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <select
          className="border rounded-md px-3 py-2"
          value={form.position_type}
          onChange={(e) =>
            update("position_type", e.target.value)
          }
        >
          <option value="LONG">Long</option>
          <option value="SHORT">Short</option>
        </select>
      </div>

      <textarea
        placeholder="Setup description"
        className="border rounded-md px-3 py-2 w-full"
        rows={3}
        value={form.setup_description}
        onChange={(e) =>
          update("setup_description", e.target.value)
        }
      />

      <div className="grid grid-cols-3 gap-4">
        <input
          placeholder="Entry Price"
          className="border rounded-md px-3 py-2"
          value={form.planned_entry_price}
          onChange={(e) =>
            update("planned_entry_price", e.target.value)
          }
        />
        <input
          placeholder="Stop Loss"
          className="border rounded-md px-3 py-2"
          value={form.planned_stop_price}
          onChange={(e) =>
            update("planned_stop_price", e.target.value)
          }
        />
        <input
          placeholder="Target"
          className="border rounded-md px-3 py-2"
          value={form.planned_target_price}
          onChange={(e) =>
            update("planned_target_price", e.target.value)
          }
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <input
          placeholder="Risk Amount"
          className="border rounded-md px-3 py-2"
          value={form.planned_risk_amount}
          onChange={(e) =>
            update("planned_risk_amount", e.target.value)
          }
        />
        <input
          placeholder="Position Size"
          className="border rounded-md px-3 py-2"
          value={form.planned_position_size}
          onChange={(e) =>
            update("planned_position_size", e.target.value)
          }
        />
      </div>

      <button
        onClick={() => onSubmit(form)}
        disabled={!form.strategy}
        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition"
      >
        Save Plan
      </button>
    </div>
  )
}
