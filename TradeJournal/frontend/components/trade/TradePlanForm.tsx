"use client";

import { useState } from "react";

export default function TradePlanForm({ onSubmit }: { onSubmit: (data: any) => void }) {
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
  });

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-sm border p-6 space-y-6">
      <h2 className="text-xl font-semibold text-gray-800">
        Create Trade Plan
      </h2>

      <div className="grid grid-cols-2 gap-4">
        <input
          type="date"
          className="border rounded-md px-3 py-2"
          value={form.plan_date}
          onChange={(e) => setForm({ ...form, plan_date: e.target.value })}
        />

        <select
          className="border rounded-md px-3 py-2"
          value={form.trade_mode}
          onChange={(e) => setForm({ ...form, trade_mode: e.target.value })}
        >
          <option value="PAPER">Paper</option>
          <option value="REAL">Real</option>
        </select>

        <input
          placeholder="Strategy (e.g. ORB)"
          className="border rounded-md px-3 py-2 col-span-2"
          onChange={(e) => setForm({ ...form, strategy: e.target.value })}
        />

        <select
          className="border rounded-md px-3 py-2"
          value={form.position_type}
          onChange={(e) => setForm({ ...form, position_type: e.target.value })}
        >
          <option value="LONG">Long</option>
          <option value="SHORT">Short</option>
        </select>
      </div>

      <textarea
        placeholder="Setup description"
        className="border rounded-md px-3 py-2 w-full"
        rows={3}
        onChange={(e) =>
          setForm({ ...form, setup_description: e.target.value })
        }
      />

      <div className="grid grid-cols-3 gap-4">
        <input placeholder="Entry Price" className="border rounded-md px-3 py-2" />
        <input placeholder="Stop Loss" className="border rounded-md px-3 py-2" />
        <input placeholder="Target" className="border rounded-md px-3 py-2" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <input placeholder="Risk Amount" className="border rounded-md px-3 py-2" />
        <input placeholder="Position Size" className="border rounded-md px-3 py-2" />
      </div>

      <button
        onClick={() => onSubmit(form)}
        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
      >
        Save Plan
      </button>
    </div>
  );
}
