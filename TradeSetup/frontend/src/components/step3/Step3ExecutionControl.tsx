// =========================================================
// File: frontend/src/components/step3/Step3ExecutionControl.tsx
// =========================================================
"use client";

import { useEffect, useRef, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type { useStep3 } from "@/hooks/useStep3";
import type { Step3StockContext } from "@/types/step3.types";

interface Step3ExecutionControlProps {
  tradeDate: TradeDate;
  step3: ReturnType<typeof useStep3>;
}

interface ManualStockRow extends Step3StockContext {}

export default function Step3ExecutionControl({
  tradeDate,
  step3,
}: Step3ExecutionControlProps) {
  const {
    snapshot,
    allowedStrategies,
    executionEnabled,
    candidates,
    candidatesMode,
    generatedAt,
    canFreeze,
    previewStep3,
    computeStep3Candidates,
    freezeStep3Candidates,
  } = step3;

  const hasPreviewed = useRef(false);

  const [stocks, setStocks] = useState<ManualStockRow[]>([
    {
      symbol: "",
      avgTradedValue20d: 0,
      atrPct: 0,
      abnormalCandle: false,
      stockOpen0915: 0,
      stockCurrentPrice: 0,
      niftyOpen0915: 0,
      niftyCurrentPrice: 0,
      gapPct: 0,
      gapHold: false,
      priceVsVwap: "ABOVE",
      structureValid: false,
    },
  ]);

  useEffect(() => {
    if (!hasPreviewed.current) {
      previewStep3();
      hasPreviewed.current = true;
    }
  }, [previewStep3]);

  const updateField = (
    index: number,
    field: keyof ManualStockRow,
    value: any
  ) => {
    const updated = [...stocks];
    updated[index] = { ...updated[index], [field]: value };
    setStocks(updated);
  };

  const addRow = () => {
    setStocks((prev) => [
      ...prev,
      {
        symbol: "",
        avgTradedValue20d: 0,
        atrPct: 0,
        abnormalCandle: false,
        stockOpen0915: 0,
        stockCurrentPrice: 0,
        niftyOpen0915: 0,
        niftyCurrentPrice: 0,
        gapPct: 0,
        gapHold: false,
        priceVsVwap: "ABOVE",
        structureValid: false,
      },
    ]);
  };

  const handleCompute = () => {
    const validStocks = stocks.filter(
      (s) => s.symbol.trim().length > 0
    );
    if (validStocks.length === 0) return;
    computeStep3Candidates(validStocks);
  };

  const DEV_FORCE_ENABLE_FREEZE = true;
  const hasAnyCandidate = candidates.length > 0;

  const effectiveCanFreeze =
    DEV_FORCE_ENABLE_FREEZE
      ? hasAnyCandidate
      : canFreeze;

  const handleFreeze = () => {
    if (!effectiveCanFreeze) return;
    freezeStep3Candidates(candidates);
  };

  const isPersisted = candidatesMode === "AUTO";

  return (
    <div className="space-y-6">

      {/* ================= STEP-3A HEADER ================= */}
      {snapshot && (
        <div className="rounded border p-4 text-sm space-y-2 bg-gray-50">
          <div className="font-semibold text-sm mb-2">
            STEP-3A — Execution Control
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>Market Context (STEP-1)</div>
            <div>{snapshot.marketContext ?? "-"}</div>

            <div>Trade Permission (STEP-2)</div>
            <div>{snapshot.tradePermission ?? "-"}</div>

            <div>Allowed Strategies</div>
            <div>
              {allowedStrategies.length
                ? allowedStrategies.join(", ")
                : "NO_TRADE"}
            </div>

            <div>Max Trades Allowed</div>
            <div>{snapshot.maxTradesAllowed}</div>

            <div>Execution Enabled</div>
            <div
              className={
                executionEnabled
                  ? "text-green-600 font-semibold"
                  : "text-red-600 font-semibold"
              }
            >
              {executionEnabled ? "YES" : "NO"}
            </div>
          </div>
        </div>
      )}

      {/* ================= STEP-3B INPUT ================= */}
      {!isPersisted && (
        <div className="rounded border p-4 space-y-6">

          <div className="font-semibold text-sm">
            STEP-3B — Stock Selection Funnel
          </div>

          {stocks.map((row, index) => (
            <div key={index} className="border rounded p-4 space-y-4">

              {/* Symbol */}
              <div>
                <input
                  type="text"
                  placeholder="Symbol"
                  value={row.symbol}
                  onChange={(e) =>
                    updateField(index, "symbol", e.target.value.toUpperCase())
                  }
                  className="border px-2 py-1 text-sm w-32"
                />
              </div>

              {/* Layer-1 */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-gray-600">
                  Layer-1 — Tradability
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <input
                    type="number"
                    placeholder="Avg Traded Value"
                    onChange={(e) =>
                      updateField(index, "avgTradedValue20d", Number(e.target.value))
                    }
                  />
                  <input
                    type="number"
                    placeholder="ATR %"
                    onChange={(e) =>
                      updateField(index, "atrPct", Number(e.target.value))
                    }
                  />
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      onChange={(e) =>
                        updateField(index, "abnormalCandle", e.target.checked)
                      }
                    />
                    Abnormal Candle
                  </label>
                </div>
              </div>

              {/* Layer-2 */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-gray-600">
                  Layer-2 — RS vs NIFTY
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <input
                    type="number"
                    placeholder="Stock Open (09:15)"
                    onChange={(e) =>
                      updateField(index, "stockOpen0915", Number(e.target.value))
                    }
                  />
                  <input
                    type="number"
                    placeholder="Stock Current"
                    onChange={(e) =>
                      updateField(index, "stockCurrentPrice", Number(e.target.value))
                    }
                  />
                  <input
                    type="number"
                    placeholder="Nifty Open (09:15)"
                    onChange={(e) =>
                      updateField(index, "niftyOpen0915", Number(e.target.value))
                    }
                  />
                  <input
                    type="number"
                    placeholder="Nifty Current"
                    onChange={(e) =>
                      updateField(index, "niftyCurrentPrice", Number(e.target.value))
                    }
                  />
                </div>
              </div>

              {/* Layer-3 */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-gray-600">
                  Layer-3 — Strategy Fit
                </div>
                <div className="grid grid-cols-4 gap-2 text-xs">
                  <input
                    type="number"
                    placeholder="Gap %"
                    onChange={(e) =>
                      updateField(index, "gapPct", Number(e.target.value))
                    }
                  />

                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      onChange={(e) =>
                        updateField(index, "gapHold", e.target.checked)
                      }
                    />
                    Gap Hold
                  </label>

                  <select
                    value={row.priceVsVwap}
                    onChange={(e) =>
                      updateField(index, "priceVsVwap", e.target.value)
                    }
                    className="border px-1 py-1"
                  >
                    <option value="ABOVE">ABOVE VWAP</option>
                    <option value="BELOW">BELOW VWAP</option>
                  </select>

                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      onChange={(e) =>
                        updateField(index, "structureValid", e.target.checked)
                      }
                    />
                    Structure Valid
                  </label>
                </div>
              </div>

            </div>
          ))}

          <div className="flex gap-4">
            <button
              onClick={addRow}
              className="text-xs text-blue-600"
            >
              + Add Stock
            </button>
            <button
              onClick={handleCompute}
              className="text-xs text-green-600 font-semibold"
            >
              Compute
            </button>
          </div>
        </div>
      )}

      {/* ================= RESULT SECTION ================= */}
      {candidates.length > 0 && (
        <div className="rounded border p-4 space-y-3">

          <div className="font-semibold text-sm">
            STEP-3 Evaluation Result
          </div>

          {candidates.map((c) => {
            const isPass = c.strategyUsed !== "NO_TRADE";

            return (
              <div key={c.symbol} className="border rounded p-3 text-sm space-y-1">
                <div className="flex justify-between">
                  <div className="font-semibold">{c.symbol}</div>
                  <div
                    className={
                      isPass
                        ? "text-green-600 font-semibold"
                        : "text-red-600 font-semibold"
                    }
                  >
                    {isPass ? "PASS" : "REJECTED"}
                  </div>
                </div>

                <div className="text-xs">Direction: {c.direction}</div>
                <div className="text-xs">Strategy: {c.strategyUsed}</div>
                <div className="text-xs text-gray-500">{c.reason}</div>
              </div>
            );
          })}

          {!isPersisted && (
            <button
              onClick={handleFreeze}
              disabled={!effectiveCanFreeze}
              className={`text-xs font-semibold ${
                effectiveCanFreeze
                  ? "text-purple-600"
                  : "text-gray-400 cursor-not-allowed"
              }`}
            >
              Freeze Candidates
            </button>
          )}

          {isPersisted && (
            <div className="text-xs text-green-600 font-semibold">
              ✓ Candidates Frozen
            </div>
          )}
        </div>
      )}

      {generatedAt && (
        <div className="text-xs text-gray-400">
          Generated at {generatedAt}
        </div>
      )}
    </div>
  );
}