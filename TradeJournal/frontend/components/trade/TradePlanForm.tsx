"use client"

import { useState } from "react"

type Props = {
  onSubmit: (payload: any) => Promise<void>
}

export default function TradePlanForm({ onSubmit }: Props) {
  const [form, setForm] = useState({
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

  const update = (k: string, v: any) =>
    setForm((p) => ({ ...p, [k]: v }))

  const submit = async () => {
    await onSubmit({
      ...form,
      planned_entry_price: Number(form.planned_entry_price),
      planned_stop_price: Number(form.planned_stop_price),
      planned_target_price: Number(form.planned_target_price || 0),
      planned_risk_amount: Number(form.planned_risk_amount),
      planned_position_size: Number(form.planned_position_size),
    })
  }

  return (
    <div className="bg-white rounded-xl border shadow-sm">
      <div className="px-6 py-4 border-b text-lg font-semibold">
        Create Trade Plan
      </div>

      <div className="px-6 py-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <input className="input" type="date" onChange={(e) => update("plan_date", e.target.value)} />
        <select className="input" onChange={(e) => update("trade_mode", e.target.value)}>
          <option value="PAPER">Paper</option>
          <option value="REAL">Real</option>
        </select>

        <input className="input" placeholder="Strategy (e.g. ORB)" onChange={(e) => update("strategy", e.target.value)} />
        <select className="input" onChange={(e) => update("position_type", e.target.value)}>
          <option value="LONG">Long</option>
          <option value="SHORT">Short</option>
        </select>

        <input className="input" placeholder="Entry Price" />
        <input className="input" placeholder="Stop Price" />
        <input className="input" placeholder="Target Price" />
        <input className="input" placeholder="Risk Amount" />
        <input className="input" placeholder="Position Size" />

        <textarea
          className="input md:col-span-2"
          placeholder="Setup Description"
          rows={3}
          onChange={(e) => update("setup_description", e.target.value)}
        />
      </div>

      <div className="px-6 py-4 border-t flex justify-end">
        <button
          onClick={submit}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Save Plan
        </button>
      </div>
    </div>
  )
}
