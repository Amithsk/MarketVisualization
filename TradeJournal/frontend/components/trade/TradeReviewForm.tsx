"use client"

import { useState } from "react"

type ReviewPayload = {
  exit_reason:
    | ""
    | "STOP_HIT"
    | "TARGET_HIT"
    | "TRAILING_STOP"
    | "MANUAL_FEAR"
    | "MANUAL_CONFUSION"
    | "RULE_VIOLATION"

  followed_entry_rules: boolean
  followed_stop_rules: boolean
  followed_position_sizing: boolean

  emotional_state:
    | "CALM"
    | "HESITANT"
    | "FEARFUL"
    | "CONFIDENT"
    | "FOMO"
    | "REVENGE"
    | "DISTRACTED"

  market_context:
    | "TRENDING"
    | "RANGE"
    | "CHOPPY"
    | "NEWS_DRIVEN"
    | "LOW_LIQUIDITY"

  learning_insight: string
  trade_grade: "A" | "B" | "C"
}

type Props = {
  onSubmit: (data: Omit<ReviewPayload, "exit_reason"> & { exit_reason: Exclude<ReviewPayload["exit_reason"], ""> }) => void
}

export default function TradeReviewForm({ onSubmit }: Props) {
  const [review, setReview] = useState<ReviewPayload>({
    exit_reason: "",
    followed_entry_rules: true,
    followed_stop_rules: true,
    followed_position_sizing: true,
    emotional_state: "CALM",
    market_context: "TRENDING",
    learning_insight: "",
    trade_grade: "A",
  })

  const isValid =
    review.exit_reason !== "" &&
    review.learning_insight.trim().length > 0

  const submit = () => {
    if (!isValid) return

    // safe cast: validated above
    onSubmit({
      ...review,
      exit_reason: review.exit_reason as Exclude<
        ReviewPayload["exit_reason"],
        ""
      >,
    })
  }

  return (
    <div className="rounded-xl border bg-white p-4 space-y-4">
      <h3 className="text-sm font-semibold tracking-wide text-gray-700">
        3 · POST-TRADE REVIEW
      </h3>

      {/* Exit reason */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Exit Reason *
        </label>
        <select
          className="w-full rounded border p-2 text-sm"
          value={review.exit_reason}
          onChange={(e) =>
            setReview({ ...review, exit_reason: e.target.value as ReviewPayload["exit_reason"] })
          }
        >
          <option value="">Select reason</option>
          <option value="STOP_HIT">Stop Hit</option>
          <option value="TARGET_HIT">Target Hit</option>
          <option value="TRAILING_STOP">Trailing Stop</option>
          <option value="MANUAL_FEAR">Manual – Fear</option>
          <option value="MANUAL_CONFUSION">Manual – Confusion</option>
          <option value="RULE_VIOLATION">Rule Violation</option>
        </select>
      </div>

      {/* Learning */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Learning / Insight *
        </label>
        <textarea
          className="w-full rounded border p-2 text-sm"
          rows={3}
          placeholder="What did you learn from this trade?"
          value={review.learning_insight}
          onChange={(e) =>
            setReview({ ...review, learning_insight: e.target.value })
          }
        />
      </div>

      {/* Submit */}
      <button
        disabled={!isValid}
        onClick={submit}
        className="w-full rounded bg-green-600 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-40"
      >
        Submit Review
      </button>
    </div>
  )
}
