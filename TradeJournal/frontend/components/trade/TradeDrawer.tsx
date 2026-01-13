"use client"

import TradePlanForm from "./TradePlanForm"
import TradeLogTable from "./TradeLogTable"
import TradeReviewForm from "./TradeReviewForm"
import { useTradeActions } from "@/hooks/useTradeActions"

type Props = {
  tradeDate: string
  onClose: () => void
}

export default function TradeDrawer({ tradeDate, onClose }: Props) {
  const trade = useTradeActions()
  const state = trade.state

  return (
    <div className="fixed right-0 top-0 z-50 h-full w-[420px] border-l bg-white p-4 shadow-lg">
      {/* Header */}
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

      {/* ================= PLAN ================= */}
      {!state && (
        <TradePlanForm
          tradeDate={tradeDate}
          onSubmit={trade.createPlan}
        />
      )}

      {/* ================= EXECUTE ================= */}
      {state?.planStatus === "PLANNED" && state.planId && (
        <button
          className="mt-4 w-full rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700"
          disabled={trade.loading}
          onClick={trade.execute}
        >
          Execute Trade
        </button>
      )}

      {/* ================= EXIT ================= */}
      {state?.planStatus === "EXECUTED" && state.tradeId && (
        <TradeLogTable
          tradeExited={!!state.tradeExited}
          onExit={trade.exit}
        />
      )}

      {/* ================= REVIEW ================= */}
      {state?.tradeExited && state.tradeId && (
        <TradeReviewForm
          reviewCompleted={!!state.reviewCompleted}
          onReviewed={trade.review}
        />
      )}
    </div>
  )
}
