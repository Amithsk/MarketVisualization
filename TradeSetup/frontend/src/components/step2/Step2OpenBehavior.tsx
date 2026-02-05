// src/components/step2/Step2OpenBehavior.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useStep2 } from "@/hooks/useStep2";
import type { TradeDate } from "@/types/common.types";
import type {
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";

interface Step2OpenBehaviorProps {
  tradeDate: TradeDate;
}

export default function Step2OpenBehavior({
  tradeDate,
}: Step2OpenBehaviorProps) {
  const {
    snapshot,
    mode,
    isFrozen,
    tradeAllowed,
    loading,
    error,
    previewStep2,
    freezeStep2,
  } = useStep2(tradeDate);

  // Manual fallback state
  const [indexOpenBehavior, setIndexOpenBehavior] =
    useState<IndexOpenBehavior>("UNKNOWN");
  const [earlyVolatility, setEarlyVolatility] =
    useState<EarlyVolatility>("UNKNOWN");
  const [marketParticipation, setMarketParticipation] =
    useState<MarketParticipation>("UNKNOWN");
  const [manualTradeAllowed, setManualTradeAllowed] =
    useState(false);

  // Auto-load STEP-2 preview
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

      {/* Loading */}
      {loading && (
        <div className="text-sm text-gray-500">
          Loading STEP-2…
        </div>
      )}

      {/* AUTO MODE (backend-driven) */}
      {mode === "AUTO" && snapshot && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded border p-4">
              <h3 className="text-sm font-semibold text-gray-700">
                Index Open
              </h3>
              <div className="mt-2 text-sm">
                {snapshot.indexOpenBehavior}
              </div>
            </div>

            <div className="rounded border p-4">
              <h3 className="text-sm font-semibold text-gray-700">
                Early Volatility
              </h3>
              <div className="mt-2 text-sm">
                {snapshot.earlyVolatility}
              </div>
            </div>

            <div className="rounded border p-4">
              <h3 className="text-sm font-semibold text-gray-700">
                Market Participation
              </h3>
              <div className="mt-2 text-sm">
                {snapshot.marketParticipation}
              </div>
            </div>
          </div>

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
        </>
      )}

      {/* MANUAL MODE (DEV fallback) */}
      {mode === "MANUAL" && !isFrozen && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded border p-4">
              <label className="text-sm font-semibold text-gray-700">
                Index Open
              </label>
              <select
                value={indexOpenBehavior}
                onChange={(e) =>
                  setIndexOpenBehavior(
                    e.target.value as IndexOpenBehavior
                  )
                }
                className="mt-2 w-full rounded border px-2 py-1 text-sm"
              >
                <option value="UNKNOWN">Unknown</option>
                <option value="STRONG_UP">Strong Up</option>
                <option value="WEAK_UP">Weak Up</option>
                <option value="FLAT">Flat</option>
                <option value="WEAK_DOWN">Weak Down</option>
                <option value="STRONG_DOWN">Strong Down</option>
              </select>
            </div>

            <div className="rounded border p-4">
              <label className="text-sm font-semibold text-gray-700">
                Early Volatility
              </label>
              <select
                value={earlyVolatility}
                onChange={(e) =>
                  setEarlyVolatility(
                    e.target.value as EarlyVolatility
                  )
                }
                className="mt-2 w-full rounded border px-2 py-1 text-sm"
              >
                <option value="UNKNOWN">Unknown</option>
                <option value="EXPANDING">Expanding</option>
                <option value="CONTRACTING">Contracting</option>
                <option value="NORMAL">Normal</option>
                <option value="CHAOTIC">Chaotic</option>
              </select>
            </div>

            <div className="rounded border p-4">
              <label className="text-sm font-semibold text-gray-700">
                Market Participation
              </label>
              <select
                value={marketParticipation}
                onChange={(e) =>
                  setMarketParticipation(
                    e.target.value as MarketParticipation
                  )
                }
                className="mt-2 w-full rounded border px-2 py-1 text-sm"
              >
                <option value="UNKNOWN">Unknown</option>
                <option value="BROAD">Broad</option>
                <option value="NARROW">Narrow</option>
                <option value="MIXED">Mixed</option>
                <option value="THIN">Thin</option>
              </select>
            </div>
          </div>

          <div className="rounded border p-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={manualTradeAllowed}
                onChange={(e) =>
                  setManualTradeAllowed(e.target.checked)
                }
              />
              Trading is permitted today
            </label>
          </div>
        </>
      )}

      {/* Freeze action / status */}
      {!isFrozen ? (
        <button
          onClick={freezeStep2}
          disabled={loading}
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

      {/* Non-blocking error note */}
      {error && mode === "MANUAL" && (
        <div className="text-xs text-gray-400">
          Backend unavailable — manual mode enabled
        </div>
      )}
    </div>
  );
}
