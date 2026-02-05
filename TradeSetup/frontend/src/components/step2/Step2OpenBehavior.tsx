// src/components/step2/Step2OpenBehavior.tsx

"use client";

import React, { useEffect } from "react";
import { useStep2 } from "@/hooks/useStep2";
import type { TradeDate } from "@/types/common.types";

interface Step2OpenBehaviorProps {
  tradeDate: TradeDate;
}

export default function Step2OpenBehavior({
  tradeDate,
}: Step2OpenBehaviorProps) {
  const {
    snapshot,
    isFrozen,
    tradeAllowed,
    loading,
    error,
    previewStep2,
    freezeStep2,
  } = useStep2(tradeDate);

  // Auto-load STEP-2 preview when component mounts
  useEffect(() => {
    previewStep2();
  }, [previewStep2]);

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Market Open Behavior for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Loading / Error */}
      {loading && (
        <div className="text-sm text-gray-500">Loading STEP-2…</div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {/* Observation grid */}
      {snapshot && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {/* Index Open */}
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Index Open
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.indexOpenBehavior}
            </div>
          </div>

          {/* Early Volatility */}
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Early Volatility
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.earlyVolatility}
            </div>
          </div>

          {/* Market Participation */}
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Market Participation
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.marketParticipation}
            </div>
          </div>
        </div>
      )}

      {/* Trade permission */}
      {snapshot && (
        <div
          className={`rounded border p-4 ${
            tradeAllowed
              ? "border-green-300 bg-green-50 text-green-700"
              : "border-red-300 bg-red-50 text-red-700"
          }`}
        >
          <div className="text-sm font-medium">
            Trade Permission
          </div>
          <div className="mt-2 text-sm">
            {tradeAllowed
              ? "Trading is permitted based on STEP-2 evaluation."
              : "Trading is NOT permitted for the day."}
          </div>
        </div>
      )}

      {/* Freeze action / status */}
      {!isFrozen ? (
        <button
          onClick={freezeStep2}
          disabled={loading || !snapshot}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Freeze STEP-2 Behavior
        </button>
      ) : (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          STEP-2 frozen at{" "}
          <span className="font-medium">
            {snapshot?.frozenAt}
          </span>
        </div>
      )}
    </div>
  );
}