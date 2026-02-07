// src/components/step1/Step1Context.tsx
"use client";

import { useEffect, useState } from "react";
import { useStep1 } from "@/hooks/useStep1";
import type { TradeDate } from "@/types/common.types";
import {
  MarketBias,
  GapContext,
  MARKET_BIAS_VALUES,
  GAP_CONTEXT_VALUES,
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

  // ✅ canonical initial values
  const [marketBias, setMarketBias] = useState<MarketBias>("UNDEFINED");
  const [gapContext, setGapContext] = useState<GapContext>("UNKNOWN");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    previewStep1();
  }, [previewStep1]);

  const handleFreeze = () => {
    freezeStep1({
      marketBias,
      premarketNotes: notes,
    });
  };

  return (
    <div className="space-y-6">
      <div className="text-sm text-gray-500">
        Pre-Market Context for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {loading && <div className="text-sm text-gray-500">Loading STEP-1…</div>}

      {/* AUTO MODE — visible but locked */}
      {mode === "AUTO" && snapshot && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded border p-4">
            <label className="text-sm font-semibold">Market Bias</label>
            <input
              value={snapshot.marketBias}
              readOnly
              className="mt-2 w-full rounded border px-2 py-1 bg-gray-100"
            />
          </div>

          <div className="rounded border p-4">
            <label className="text-sm font-semibold">Gap Context</label>
            <input
              value={snapshot.gapContext}
              readOnly
              className="mt-2 w-full rounded border px-2 py-1 bg-gray-100"
            />
          </div>

          <div className="rounded border p-4">
            <label className="text-sm font-semibold">Pre-Market Notes</label>
            <textarea
              value={snapshot.premarketNotes ?? ""}
              readOnly
              className="mt-2 w-full rounded border px-2 py-1 bg-gray-100"
            />
          </div>
        </div>
      )}

      {/* MANUAL MODE */}
      {mode === "MANUAL" && !isFrozen && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded border p-4">
            <label className="text-sm font-semibold">Market Bias</label>
            <select
              value={marketBias}
              onChange={(e) =>
                setMarketBias(e.target.value as MarketBias)
              }
              className="mt-2 w-full rounded border px-2 py-1"
            >
              {MARKET_BIAS_VALUES.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded border p-4">
            <label className="text-sm font-semibold">Gap Context</label>
            <select
              value={gapContext}
              onChange={(e) =>
                setGapContext(e.target.value as GapContext)
              }
              className="mt-2 w-full rounded border px-2 py-1"
            >
              {GAP_CONTEXT_VALUES.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded border p-4">
            <label className="text-sm font-semibold">Pre-Market Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="mt-2 w-full rounded border px-2 py-1"
              rows={3}
            />
          </div>
        </div>
      )}

      {!isFrozen ? (
        <button
          onClick={handleFreeze}
          disabled={loading}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white"
        >
          Freeze STEP-1 Context
        </button>
      ) : (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          STEP-1 frozen at {snapshot?.frozenAt}
        </div>
      )}

      {error && mode === "MANUAL" && (
        <div className="text-xs text-gray-400">
          Backend unavailable — manual mode enabled
        </div>
      )}
    </div>
  );
}
