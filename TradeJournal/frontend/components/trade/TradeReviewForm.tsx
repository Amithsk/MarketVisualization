"use client"

import { useState } from "react"

type Props = {
  onSubmit: (payload: any) => Promise<void>
}

export default function TradeReviewForm({ onSubmit }: Props) {
  const [form, setForm] = useState({
    exit_reason: "",
    followed_entry_rules: true,
    followed_stop_rules: true,
    followed_position_sizing: true,
    emotional_state: "CALM",
    market_context: "TRENDING",
    learning_insight: "",
    trade_grade: "A",
  })

  const update = (k: string, v: any) =>
    setForm((p) => ({ ...p, [k]: v }))

  return (
    <div className="bg-white rounded-xl border shadow-sm">
      <div className="px-6 py-4 border-b text-lg font-semibold">
        Trade Review
      </div>

      <div className="px-6 py-4 space-y-4">
        <select className="input" onChange={(e) => update("exit_reason", e.target.value)}>
          <option value="">Exit Reason</option>
          <option value="STOP_HIT">Stop Hit</option>
          <option value="TARGET_HIT">Target Hit</option>
        </select>

        <select className="input" onChange={(e) => update("emotional_state", e.target.value)}>
          <option>CALM</option>
          <option>HESITANT</option>
          <option>FEARFUL</option>
          <option>CONFIDENT</option>
        </select>

        <textarea
          className="input"
          placeholder="Learning Insight"
          rows={3}
          onChange={(e) => update("learning_insight", e.target.value)}
        />

        <select className="input" onChange={(e) => update("trade_grade", e.target.value)}>
          <option>A</option>
          <option>B</option>
          <option>C</option>
        </select>
      </div>

      <div className="px-6 py-4 border-t flex justify-end">
        <button
          onClick={() => onSubmit(form)}
          className="px-4 py-2 bg-purple-600 text-white rounded"
        >
          Submit Review
        </button>
      </div>
    </div>
  )
}
