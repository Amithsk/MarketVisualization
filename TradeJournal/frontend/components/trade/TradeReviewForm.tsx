"use client"

import { useState } from "react"

type Props = {
  reviewCompleted?: boolean
  onReviewed: (payload: {
    exit_reason: string
    followed_entry_rules: boolean
    followed_stop_rules: boolean
    followed_position_sizing: boolean
    emotional_state: string
    market_context: string
    learning_insight: string
    trade_grade: "A" | "B" | "C"
  }) => Promise<void>
}

export default function TradeReviewForm({ reviewCompleted, onReviewed }: Props) {
  const [exitReason, setExitReason] = useState("STOP_HIT")

  const [followedEntry, setFollowedEntry] = useState(true)
  const [followedStop, setFollowedStop] = useState(true)
  const [followedSizing, setFollowedSizing] = useState(true)

  const [emotionalState, setEmotionalState] = useState("CALM")
  const [marketContext, setMarketContext] = useState("TRENDING")
  const [learningInsight, setLearningInsight] = useState("")
  const [tradeGrade, setTradeGrade] = useState<"A" | "B" | "C">("A")

  if (reviewCompleted) {
    return (
      <div className="mt-4 rounded bg-green-50 p-3 text-sm text-green-700">
        ✅ Review submitted
      </div>
    )
  }

  return (
    <div className="mt-4 space-y-3 border-t pt-4">
      <h3 className="text-sm font-semibold">Post-Trade Review</h3>

      {/* EXIT REASON (MANDATORY) */}
      <div>
        <label className="text-xs font-medium">Exit Reason</label>
        <select
          className="w-full rounded border px-2 py-1 text-sm"
          value={exitReason}
          onChange={(e) => setExitReason(e.target.value)}
        >
          <option value="STOP_HIT">Stop Hit</option>
          <option value="TARGET_HIT">Target Hit</option>
          <option value="TRAILING_STOP">Trailing Stop</option>
          <option value="MANUAL_FEAR">Manual – Fear</option>
          <option value="MANUAL_CONFUSION">Manual – Confusion</option>
          <option value="RULE_VIOLATION">Rule Violation</option>
        </select>
      </div>

      {/* CHECKBOXES */}
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={followedEntry}
          onChange={(e) => setFollowedEntry(e.target.checked)}
        />
        Followed entry rules
      </label>

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={followedStop}
          onChange={(e) => setFollowedStop(e.target.checked)}
        />
        Followed stop rules
      </label>

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={followedSizing}
          onChange={(e) => setFollowedSizing(e.target.checked)}
        />
        Followed position sizing
      </label>

      {/* EMOTIONAL STATE */}
      <div>
        <label className="text-xs font-medium">Emotional State</label>
        <select
          className="w-full rounded border px-2 py-1 text-sm"
          value={emotionalState}
          onChange={(e) => setEmotionalState(e.target.value)}
        >
          <option value="CALM">Calm</option>
          <option value="HESITANT">Hesitant</option>
          <option value="FEARFUL">Fearful</option>
          <option value="CONFIDENT">Confident</option>
          <option value="FOMO">FOMO</option>
          <option value="REVENGE">Revenge</option>
          <option value="DISTRACTED">Distracted</option>
        </select>
      </div>

      {/* MARKET CONTEXT */}
      <div>
        <label className="text-xs font-medium">Market Context</label>
        <select
          className="w-full rounded border px-2 py-1 text-sm"
          value={marketContext}
          onChange={(e) => setMarketContext(e.target.value)}
        >
          <option value="TRENDING">Trending</option>
          <option value="RANGE">Range</option>
          <option value="CHOPPY">Choppy</option>
          <option value="NEWS_DRIVEN">News Driven</option>
          <option value="LOW_LIQUIDITY">Low Liquidity</option>
        </select>
      </div>

      {/* LEARNING */}
      <textarea
        className="w-full rounded border p-2 text-sm"
        placeholder="What did you learn?"
        value={learningInsight}
        onChange={(e) => setLearningInsight(e.target.value)}
      />

      {/* GRADE */}
      <div>
        <label className="text-xs font-medium">Trade Grade</label>
        <select
          className="w-full rounded border px-2 py-1 text-sm"
          value={tradeGrade}
          onChange={(e) => setTradeGrade(e.target.value as "A" | "B" | "C")}
        >
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
        </select>
      </div>

      <button
        className="w-full rounded bg-purple-600 px-3 py-2 text-sm text-white hover:bg-purple-700"
        onClick={() =>
          onReviewed({
            exit_reason: exitReason,
            followed_entry_rules: followedEntry,
            followed_stop_rules: followedStop,
            followed_position_sizing: followedSizing,
            emotional_state: emotionalState,
            market_context: marketContext,
            learning_insight: learningInsight,
            trade_grade: tradeGrade,
          })
        }
      >
        Submit Review
      </button>
    </div>
  )
}
