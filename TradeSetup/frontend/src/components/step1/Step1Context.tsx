// src/components/step1/Step1Context.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useStep1 } from "@/hooks/useStep1";
import type { TradeDate } from "@/types/common.types";
import type {
  MarketBias,
  GapContext,
} from "@/types/step1.types";

interface Step1ContextProps {
  tradeDate: TradeDate;
}

export default function Step1Context({ tradeDate }: Step1ContextProps) {
  const {
    snapshot,
    mode,
    isFrozen,
    loading,
    error,
    previewStep1,
    freezeStep1,
  } = useStep1(tradeDate);

  // Manual input state (DEV fallback)
  const [marketBias, setMarketBias] =
    useState<MarketBias>("UNDEFINED");
  const [gapContext, setGapContext] =
    useState<GapContext>("UNKNOWN");
  const [notes, setNotes] = useState("");

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

      {/* Loading */}
      {loading && (
        <div className="text-sm text-gray-500">
          Loading STEP-1…
        </div>
      )}

      {/* AUTO MODE (backend data available) */}
      {mode === "AUTO" && snapshot && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Market Bias
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.marketBias}
            </div>
          </div>

          <div className="rounded border p-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Gap Context
            </h3>
            <div className="mt-2 text-sm">
              {snapshot.gapContext}
            </div>
          </div>

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

      {/* MANUAL MODE (DEV fallback) */}
      {mode === "MANUAL" && !isFrozen && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded border p-4">
            <label className="text-sm font-semibold text-gray-700">
              Market Bias
            </label>
            <select
              value={marketBias}
              onChange={(e) =>
                setMarketBias(e.target.value as MarketBias)
              }
              className="mt-2 w-full rounded border px-2 py-1 text-sm"
            >
              <option value="UNDEFINED">Undefined</option>
              <option value="BULLISH">Bullish</option>
              <option value="BEARISH">Bearish</option>
              <option value="NEUTRAL">Neutral</option>
              <option value="RANGE_BOUND">Range Bound</option>
            </select>
          </div>

          <div className="rounded border p-4">
            <label className="text-sm font-semibold text-gray-700">
              Gap Context
            </label>
            <select
              value={gapContext}
              onChange={(e) =>
                setGapContext(e.target.value as GapContext)
              }
              className="mt-2 w-full rounded border px-2 py-1 text-sm"
            >
              <option value="UNKNOWN">Unknown</option>
              <option value="GAP_UP">Gap Up</option>
              <option value="GAP_DOWN">Gap Down</option>
              <option value="FLAT">Flat</option>
            </select>
          </div>

          <div className="rounded border p-4">
            <label className="text-sm font-semibold text-gray-700">
              Pre-Market Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="mt-2 w-full rounded border px-2 py-1 text-sm"
              rows={3}
              placeholder="Your observations before market open…"
            />
          </div>
        </div>
      )}

      {/* Freeze action / status */}
      {!isFrozen ? (
        <button
          onClick={freezeStep1}
          disabled={loading}
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

      {/* Error shown only for debugging, not blocking */}
      {error && mode === "MANUAL" && (
        <div className="text-xs text-gray-400">
          Backend unavailable — manual mode enabled
        </div>
      )}
    </div>
  );
}
