"use client";

import { useState } from "react";

export default function TradeReviewForm({ onSubmit }: { onSubmit: (data: any) => void }) {
  const [review, setReview] = useState({
    exit_reason: "",
    followed_entry_rules: true,
    followed_stop_rules: true,
    followed_position_sizing: true,
    emotional_state: "CALM",
    market_context: "TRENDING",
    learning_insight: "",
    trade_grade: "A",
  });

  return (
    <div className="bg-white border rounded-xl p-6 space-y-4">
      <h3 className="text-lg font-semibold">Post-Trade Review</h3>

      <select
        className="border rounded-md px-3 py-2 w-full"
        onChange={(e) => setReview({ ...review, exit_reason: e.target.value })}
      >
        <option value="">Exit Reason</option>
        <option value="STOP_HIT">Stop Hit</option>
        <option value="TARGET_HIT">Target Hit</option>
      </select>

      <textarea
        placeholder="What did you learn?"
        className="border rounded-md px-3 py-2 w-full"
        rows={3}
        onChange={(e) =>
          setReview({ ...review, learning_insight: e.target.value })
        }
      />

      <button
        onClick={() => onSubmit(review)}
        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
      >
        Submit Review
      </button>
    </div>
  );
}
