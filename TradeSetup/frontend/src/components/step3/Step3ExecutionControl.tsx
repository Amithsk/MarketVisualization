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

  // =========================
  // Initial Preview
  // =========================
  useEffect(() => {
    if (!hasPreviewed.current) {
      previewStep3();
      hasPreviewed.current = true;
    }
  }, [previewStep3]);

  // =========================
  // SYNC PREVIEW → FORM STATE
  // =========================
  useEffect(() => {
    if (!snapshot) return;
    if (candidatesMode !== "MANUAL") return;
    if (!snapshot.candidates || snapshot.candidates.length === 0) return;

    const hasManualInput =
      stocks.length > 1 || stocks[0]?.symbol?.trim().length > 0;

    if (hasManualInput) return;

    const mapped: ManualStockRow[] = snapshot.candidates.map((c: any) => ({
      symbol: c.symbol ?? "",
      avgTradedValue20d:
        c.avgTradedValue20d ??
        c.avg_traded_value_20d ??
        0,
      atrPct:
        c.atrPct ??
        c.atr_pct ??
        0,
      abnormalCandle:
        c.abnormalCandle ??
        c.abnormal_candle ??
        false,
      stockOpen0915: 0,
      stockCurrentPrice: 0,
      niftyOpen0915: 0,
      niftyCurrentPrice: 0,
      gapPct: 0,
      gapHold: false,
      priceVsVwap: "ABOVE" as "ABOVE",
      structureValid: false,
    }));

    setStocks(mapped);
  }, [snapshot?.generatedAt]);

  const isLocked = canFreeze || candidatesMode === "AUTO";
  const isPersisted = candidatesMode === "AUTO";

  const updateField = (
    index: number,
    field: keyof ManualStockRow,
    value: any
  ) => {
    if (isLocked) return;
    const updated = [...stocks];
    updated[index] = { ...updated[index], [field]: value };
    setStocks(updated);
  };

  const addRow = () => {
    if (isLocked) return;
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
    if (isLocked) return;
    const validStocks = stocks.filter(
      (s) => s.symbol.trim().length > 0
    );
    if (validStocks.length === 0) return;
    computeStep3Candidates(validStocks);
  };

  const handleFreeze = () => {
    if (!canFreeze) return;
    freezeStep3Candidates(candidates);
  };

  return (
    <div className="space-y-6">

      {/* ================= STEP-3A ================= */}
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
            <div className={executionEnabled ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
              {executionEnabled ? "YES" : "NO"}
            </div>
          </div>
        </div>
      )}

      {/* ================= STEP-3B ================= */}
      {!isPersisted && (
        <div className="rounded border p-4 space-y-6">
          <div className="font-semibold text-sm">
            STEP-3B — Stock Selection Funnel
          </div>

          {stocks.map((row, index) => (
            <div key={index} className="border rounded p-4 space-y-6">

              {/* Symbol */}
              <div>
                <label className="text-xs text-gray-500 block mb-1">
                  Stock Symbol
                </label>
                <input
                  type="text"
                  value={row.symbol}
                  disabled={isLocked}
                  onChange={(e) =>
                    updateField(index, "symbol", e.target.value.toUpperCase())
                  }
                  className="border px-2 py-1 text-sm w-40"
                />
              </div>

              {/* Layer-1 */}
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-2">
                  Layer-1 — Tradability
                </div>

                <div className="grid grid-cols-3 gap-4 text-xs">

                  <div>
                    <label className="block mb-1 text-gray-500">
                      Avg Traded Value (20D ₹)
                    </label>
                    <input
                      type="number"
                      value={row.avgTradedValue20d}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "avgTradedValue20d", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                  <div>
                    <label className="block mb-1 text-gray-500">
                      ATR % (14D)
                    </label>
                    <input
                      type="number"
                      value={row.atrPct}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "atrPct", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                  <div className="flex items-center gap-2 mt-6">
                    <input
                      type="checkbox"
                      checked={row.abnormalCandle}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "abnormalCandle", e.target.checked)
                      }
                    />
                    <span className="text-gray-500">
                      Abnormal Candle (Range {'>'} 2× ATR)
                    </span>
                  </div>

                </div>
              </div>

              {/* Layer-2 */}
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-2">
                  Layer-2 — Relative Strength vs NIFTY
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs">

                  <div>
                    <label className="block mb-1 text-gray-500">
                      Stock Open (09:15)
                    </label>
                    <input
                      type="number"
                      value={row.stockOpen0915}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "stockOpen0915", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                  <div>
                    <label className="block mb-1 text-gray-500">
                      Stock Current Price
                    </label>
                    <input
                      type="number"
                      value={row.stockCurrentPrice}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "stockCurrentPrice", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                  <div>
                    <label className="block mb-1 text-gray-500">
                      NIFTY Open (09:15)
                    </label>
                    <input
                      type="number"
                      value={row.niftyOpen0915}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "niftyOpen0915", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                  <div>
                    <label className="block mb-1 text-gray-500">
                      NIFTY Current Price
                    </label>
                    <input
                      type="number"
                      value={row.niftyCurrentPrice}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "niftyCurrentPrice", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                </div>
              </div>

              {/* Layer-3 */}
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-2">
                  Layer-3 — Strategy Fit
                </div>

                <div className="grid grid-cols-4 gap-4 text-xs">

                  <div>
                    <label className="block mb-1 text-gray-500">
                      Gap % (Open vs Prev Close)
                    </label>
                    <input
                      type="number"
                      value={row.gapPct}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "gapPct", Number(e.target.value))
                      }
                      className="border px-2 py-1 w-full"
                    />
                  </div>

                  <div className="flex items-center gap-2 mt-6">
                    <input
                      type="checkbox"
                      checked={row.gapHold}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "gapHold", e.target.checked)
                      }
                    />
                    <span className="text-gray-500">
                      Gap Hold
                    </span>
                  </div>

                  <div>
                    <label className="block mb-1 text-gray-500">
                      Price vs VWAP
                    </label>
                    <select
                      value={row.priceVsVwap}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "priceVsVwap", e.target.value as "ABOVE" | "BELOW")
                      }
                      className="border px-1 py-1 w-full"
                    >
                      <option value="ABOVE">ABOVE VWAP</option>
                      <option value="BELOW">BELOW VWAP</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-2 mt-6">
                    <input
                      type="checkbox"
                      checked={row.structureValid}
                      disabled={isLocked}
                      onChange={(e) =>
                        updateField(index, "structureValid", e.target.checked)
                      }
                    />
                    <span className="text-gray-500">
                      Structure Valid
                    </span>
                  </div>

                </div>
              </div>

            </div>
          ))}

          {!isLocked && (
            <div className="flex gap-4">
              <button onClick={addRow} className="text-xs text-blue-600">
                + Add Stock
              </button>
              <button onClick={handleCompute} className="text-xs text-green-600 font-semibold">
                Compute
              </button>
            </div>
          )}
        </div>
      )}

      {/* ================= RESULT ================= */}
      {(canFreeze || candidatesMode === "AUTO") && candidates.length > 0 && (
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
                  <div className={isPass ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
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
              disabled={!canFreeze}
              className={`text-xs font-semibold ${
                canFreeze
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