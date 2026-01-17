"use client"

import TradePlanCard from "./TradePlanCard"
import TradeExitForm from "./TradeExitForm"
import TradeReviewForm from "./TradeReviewForm"

import { TradePlan } from "@/types/trade"

type Props = {
  plans: TradePlan[]
  loading: boolean
  onExecute: (planId: number) => void
  onExit: (tradeId: number, payload: any) => void
  onReview: (tradeId: number, payload: any) => void
}

export default function TradePlanList({
  plans,
  loading,
  onExecute,
  onExit,
  onReview,
}: Props) {
  if (!plans.length) {
    return (
      <div className="text-sm text-gray-500 mt-4">
        No trade plans for this day.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {plans.map((plan) => (
        <div
          key={plan.id}
          className="rounded border bg-white p-3 shadow-sm"
        >
          <TradePlanCard plan={plan} />

          {/* EXECUTE */}
          {plan.plan_status === "PLANNED" && (
            <button
              className="mt-3 w-full rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
              onClick={() => onExecute(plan.id)}
            >
              Execute Trade
            </button>
          )}

          {/* EXIT */}
          {plan.plan_status === "EXECUTED" && plan.trade_id && (
            <div className="mt-3">
              <TradeExitForm
                onSubmit={(payload) =>
                  onExit(plan.trade_id!, payload)
                }
              />
            </div>
          )}

          {/* REVIEW */}
          {plan.plan_status === "EXECUTED" && plan.trade_id && (
            <div className="mt-3">
              <TradeReviewForm
                onSubmit={(payload) =>
                  onReview(plan.trade_id!, payload)
                }
              />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
