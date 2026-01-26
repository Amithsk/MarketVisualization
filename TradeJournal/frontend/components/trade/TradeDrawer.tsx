"use client"

import { useState } from "react"

import TradePlanForm from "./TradePlanForm"
import TradePlanCard from "./TradePlanCard"
import TradeExitForm from "./TradeExitForm"
import TradeReviewForm from "./TradeReviewForm"

import { useTradeActions } from "@/hooks/useTradeActions"
import { TradePlan } from "@/types/trade"

type Props = {
  tradeDate: string
  onClose: () => void
}

export default function TradeDrawer({ tradeDate, onClose }: Props) {
  const {
    plans,
    loading,
    error,
    canExecuteMoreTrades,
    createPlan,
    executePlan,
    exitTrade,
    submitTradeReview,
  } = useTradeActions(tradeDate)

  // which plan is expanded
  const [expandedPlanId, setExpandedPlanId] = useState<number | null>(null)

  const toggleExpand = (planId: number) => {
    setExpandedPlanId((prev) => (prev === planId ? null : planId))
  }

  return (
    <div className="fixed right-0 top-0 z-50 h-full w-[420px] overflow-y-auto border-l bg-white p-4 shadow-lg">
      {/* ================= HEADER ================= */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Trading Day · {tradeDate}
        </h2>
        <button
          className="text-sm text-gray-500 hover:text-black"
          onClick={onClose}
        >
          ✕
        </button>
      </div>

      {/* ================= ERROR ================= */}
      {error && (
        <div className="mb-3 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* ================= CREATE PLAN ================= */}
      {canExecuteMoreTrades && (
        <div className="mb-6">
          <TradePlanForm
            onSubmit={(payload) =>
              createPlan({
                ...payload,
                plan_date: tradeDate,
              })
            }
          />
        </div>
      )}

      {/* ================= PLAN LIST ================= */}
      <div className="space-y-3">
        {plans.map((plan: TradePlan) => {
          const isExpanded = expandedPlanId === plan.id

          return (
            <div
              key={plan.id}
              className="rounded-lg border bg-white"
            >
              {/* -------- SUMMARY (CLICKABLE) -------- */}
              <button
                onClick={() => toggleExpand(plan.id)}
                className="w-full text-left p-3"
              >
                <TradePlanCard plan={plan} />
              </button>

              {/* -------- EXPANDED CONTENT -------- */}
              {isExpanded && (
                <div className="border-t px-3 pb-3">
                  {/* EXECUTE */}
                  {plan.plan_status === "PLANNED" && (
                    <button
                      className="mt-3 w-full rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                      disabled={loading || !canExecuteMoreTrades}
                      onClick={() => executePlan(plan.id)}
                    >
                      Execute Trade
                    </button>
                  )}

                  {/* EXIT */}
                  {plan.plan_status === "EXECUTED" && plan.trade_id && (
                    <div className="mt-4">
                      <TradeExitForm
                        onSubmit={(payload) =>
                          exitTrade(plan.trade_id!, payload)
                        }
                      />
                    </div>
                  )}

                  {/* REVIEW */}
                  {plan.plan_status === "EXECUTED" && plan.trade_id && (
                    <div className="mt-4">
                      <TradeReviewForm
                        onSubmit={(payload) =>
                          submitTradeReview(plan.trade_id!, {
                            ...payload,
                            symbol: plan.symbol, // required
                          })
                        }
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}

        {!loading && plans.length === 0 && (
          <div className="text-sm text-gray-500">
            No trade plans created for this day.
          </div>
        )}
      </div>
    </div>
  )
}
