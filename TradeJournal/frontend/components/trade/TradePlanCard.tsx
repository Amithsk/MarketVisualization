"use client"

import { TradePlan } from "@/types/trade"

type Props = {
  plan: TradePlan
}

export default function TradePlanCard({ plan }: Props) {
  return (
    <div className="rounded-lg border bg-white p-3 hover:bg-gray-50">
      {/* TOP ROW */}
      <div className="flex items-center justify-between">
        <span className="font-semibold text-sm">
          {plan.strategy}
        </span>

        <span
          className={`text-xs rounded px-2 py-0.5 ${
            plan.plan_status === "EXECUTED"
              ? "bg-green-100 text-green-700"
              : plan.plan_status === "PLANNED"
              ? "bg-blue-100 text-blue-700"
              : "bg-gray-100 text-gray-600"
          }`}
        >
          {plan.plan_status}
        </span>
      </div>

      {/* META */}
      <div className="mt-1 text-xs text-gray-600">
        {plan.position_type}
        {plan.trade_mode && ` · ${plan.trade_mode}`}
      </div>

      {/* PRICE SUMMARY */}
      {plan.planned_entry_price !== undefined && (
        <div className="mt-1 text-xs text-gray-500">
          Entry: {plan.planned_entry_price} ·
          Stop: {plan.planned_stop_price} ·
          Target: {plan.planned_target_price}
        </div>
      )}

      {/* NOT TAKEN */}
      {plan.not_taken_reason && (
        <div className="mt-1 text-xs text-red-600">
          Not taken: {plan.not_taken_reason}
        </div>
      )}
    </div>
  )
}
