"use client"

import { TradePlan } from "@/types/trade"

type Props = {
  plan: TradePlan
}

export default function TradePlanCard({ plan }: Props) {
  return (
    <div className="space-y-1 text-sm">
      <div className="flex items-center justify-between">
        <span className="font-medium">{plan.strategy}</span>
        <span className="text-xs rounded bg-gray-100 px-2 py-0.5">
          {plan.plan_status}
        </span>
      </div>

      <div className="text-gray-600">
        {plan.position_type}
        {plan.trade_mode && ` · ${plan.trade_mode}`}
      </div>

      {plan.planned_entry_price && (
        <div className="text-gray-500">
          Entry: {plan.planned_entry_price} ·
          Stop: {plan.planned_stop_price} ·
          Target: {plan.planned_target_price}
        </div>
      )}

      {plan.not_taken_reason && (
        <div className="text-xs text-red-600">
          Not taken: {plan.not_taken_reason}
        </div>
      )}
    </div>
  )
}
