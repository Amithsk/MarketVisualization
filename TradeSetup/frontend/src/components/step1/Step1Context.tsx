// src/components/step1/Step1Context.tsx

"use client";

import React, { useEffect } from "react";
import { useStep1 } from "@/hooks/useStep1";
import type { TradeDate } from "@/types/common.types";

interface Step1ContextProps {
  tradeDate: TradeDate;
}

export default function Step1Context({ tradeDate }: Step1ContextProps) {
  const {
    snapshot,
    isFrozen,
    loading,
    error,
    previewStep1,
    freezeStep1,
  } = useStep1(tradeDate);

  // Auto-load preview on mount
  useEffect(() => {
    previewStep1();
  }, [previewStep1]);

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Pre-Market Context for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Loading / Error */}
      {loading && (
        <div className="text-sm text-gray-500">Loading STEP-1…</div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {/* Snapshot grid */}
      {snapshot && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {/* Market Bias */}
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Market Bias
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.marketBias}
            </div>
          </div>

          {/* Gap Context */}
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Gap Context
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.gapContext}
            </div>
          </div>

          {/* Pre-Market Notes */}
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Pre-Market Notes
            </h3>
            <div className="mt-2 text-sm text-gray-600 whitespace-pre-wrap">
              {snapshot.preMarketNotes || "No notes added"}
            </div>
          </div>
        </div>
      )}

      {/* Freeze action / status */}
      {!isFrozen ? (
        <button
          onClick={freezeStep1}
          disabled={loading || !snapshot}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Freeze STEP-1 Context
        </button>
      ) : (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          STEP-1 frozen at{" "}
          <span className="font-medium">
            {snapshot?.frozenAt}
          </span>
        </div>
      )}
    </div>
  );
}