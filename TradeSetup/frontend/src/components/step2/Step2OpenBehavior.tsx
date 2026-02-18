"use client";

import { useMemo, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type { useStep2 } from "@/hooks/useStep2";
import type { Step2CandleInput } from "@/types/step2.types";

interface Step2OpenBehaviorProps {
  tradeDate: TradeDate;
  step2: ReturnType<typeof useStep2>;
}

/**
 * STEP-2 Open Behavior
 *
 * Hybrid Manual Mode (Automation Ready)
 *
 * Phase-1:
 *  - avg_5m_range_prev_day manually entered
 *
 * Future:
 *  - backend auto-derives baseline
 *  - UI automatically switches to read-only
 */

export default function Step2OpenBehavior({
  tradeDate,
  step2,
}: Step2OpenBehaviorProps) {
  const {
    snapshot,
    isFrozen,
    manualInputRequired,
    tradeAllowed,
    loading,
    error,
    computeStep2,
    freezeStep2,
  } = step2;

  /* =====================================================
     Baseline (Hybrid Mode Support)
  ===================================================== */

  const [manualBaseline, setManualBaseline] = useState<number>(0);

  const baselineValue =
    snapshot?.avg_5m_range_prev_day ?? manualBaseline;

  const isManualMode = manualInputRequired === true;

  /* =====================================================
     Candle Grid (09:15–09:45)
  ===================================================== */

  const initialCandles: Step2CandleInput[] = [
    "09:15",
    "09:20",
    "09:25",
    "09:30",
    "09:35",
    "09:40",
    "09:45",
  ].map((t) => ({
    timestamp: t,
    open: 0,
    high: 0,
    low: 0,
    close: 0,
    volume: 0,
  }));

  const [candles, setCandles] =
    useState<Step2CandleInput[]>(initialCandles);

  const [reason, setReason] = useState("");

  const updateCandle = (
    index: number,
    field: keyof Step2CandleInput,
    value: number
  ) => {
    setCandles((prev) => {
      const updated = [...prev];
      updated[index] = {
        ...updated[index],
        [field]: value,
      };
      return updated;
    });
  };

  /* =====================================================
     Validation
  ===================================================== */

  const candlesValid = useMemo(() => {
    return candles.every(
      (c) =>
        c.open > 0 &&
        c.high > 0 &&
        c.low > 0 &&
        c.close > 0 &&
        c.volume > 0
    );
  }, [candles]);

  const analyticsReady =
    snapshot &&
    snapshot.ir_high !== null &&
    snapshot.ir_high !== undefined;

  /* =====================================================
     Actions
  ===================================================== */

  const handleCompute = () => {
    if (!candlesValid) return;

    computeStep2({
      candles,
      avg5mRangePrevDay: baselineValue,
    });
  };

  const handleFreeze = () => {
    if (!analyticsReady) return;

    freezeStep2({
      candles,
      avg5mRangePrevDay: baselineValue,
      reason,
    });
  };

  /* =====================================================
     UI
  ===================================================== */

  return (
    <div className="space-y-8">
      <div className="text-sm text-gray-500">
        Market Open Behavior for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {loading && (
        <div className="text-sm text-gray-500">
          Processing…
        </div>
      )}

      {/* =====================================================
         PREVIOUS DAY BASELINE
      ===================================================== */}
      <div className="rounded border p-4 space-y-3">
        <h3 className="text-sm font-semibold text-gray-700">
          Previous Day Baseline
        </h3>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">
            Avg 5-min Range (Prev Day)
          </span>

          {isManualMode && !isFrozen ? (
            <input
              type="number"
              min="0"
              value={baselineValue}
              onChange={(e) =>
                setManualBaseline(Number(e.target.value))
              }
              className="w-32 rounded border px-2 py-1 text-sm"
            />
          ) : (
            <span className="font-medium">
              {baselineValue ?? "--"}
            </span>
          )}
        </div>
      </div>

      {/* =====================================================
         MANUAL INPUT GRID
      ===================================================== */}
      {manualInputRequired && !isFrozen && (
        <div className="rounded border p-4 space-y-4">
          <h3 className="text-sm font-semibold text-gray-700">
            5-Minute Candle Input (09:15–09:45)
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-sm border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2 border">Time</th>
                  <th className="p-2 border">Open</th>
                  <th className="p-2 border">High</th>
                  <th className="p-2 border">Low</th>
                  <th className="p-2 border">Close</th>
                  <th className="p-2 border">Volume</th>
                </tr>
              </thead>
              <tbody>
                {candles.map((c, i) => (
                  <tr key={c.timestamp}>
                    <td className="p-2 border">{c.timestamp}</td>
                    {(
                      ["open", "high", "low", "close", "volume"] as const
                    ).map((field) => (
                      <td key={field} className="p-2 border">
                        <input
                          type="number"
                          min="0"
                          className="w-full rounded border px-1 py-0.5"
                          value={c[field]}
                          onChange={(e) =>
                            updateCandle(
                              i,
                              field,
                              Number(e.target.value)
                            )
                          }
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={handleCompute}
            disabled={!candlesValid || loading}
            className="rounded bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            Compute Analytical Breakdown
          </button>
        </div>
      )}

      {/* =====================================================
         ANALYTICAL BREAKDOWN
      ===================================================== */}
      {analyticsReady && (
        <div className="rounded border p-4 space-y-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Analytical Breakdown (Backend Derived)
          </h3>

          <Metric label="IR High" value={snapshot.ir_high} />
          <Metric label="IR Low" value={snapshot.ir_low} />
          <Metric label="IR Range" value={snapshot.ir_range} />
          <Metric label="IR Ratio" value={snapshot.ir_ratio} />
          <Metric label="Volatility State" value={snapshot.volatility_state} />
          <Metric label="VWAP Cross Count" value={snapshot.vwap_cross_count} />
          <Metric label="VWAP State" value={snapshot.vwap_state} />
          <Metric label="Range Hold Status" value={snapshot.range_hold_status} />

          <hr />

          <Metric label="Index Open Behavior" value={snapshot.index_open_behavior} />
          <Metric label="Early Volatility" value={snapshot.early_volatility} />
          <Metric label="Market Participation" value={snapshot.market_participation} />

          <TradePermissionBanner tradeAllowed={tradeAllowed ?? false} />
        </div>
      )}

      {/* =====================================================
         FREEZE SECTION
      ===================================================== */}
      {!isFrozen && analyticsReady && (
        <div className="rounded border p-4 space-y-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Freeze STEP-2
          </h3>

          <textarea
            placeholder="One factual sentence linking observation → decision"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            className="w-full rounded border px-2 py-1 text-sm"
          />

          <button
            onClick={handleFreeze}
            disabled={loading || reason.trim().length === 0}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            Freeze STEP-2 Behavior
          </button>
        </div>
      )}

      {isFrozen && (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          STEP-2 frozen at{" "}
          <span className="font-medium">
            {snapshot?.frozen_at}
          </span>
        </div>
      )}

      {error && (
        <div className="text-xs text-red-500">
          Backend error occurred.
        </div>
      )}
    </div>
  );
}

/* =====================================================
   Small UI Helpers
===================================================== */

function Metric({
  label,
  value,
}: {
  label: string;
  value: any;
}) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{value ?? "--"}</span>
    </div>
  );
}

function TradePermissionBanner({
  tradeAllowed,
}: {
  tradeAllowed: boolean;
}) {
  return (
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
          ? "Trading is permitted."
          : "Trading is NOT permitted."}
      </div>
    </div>
  );
}
