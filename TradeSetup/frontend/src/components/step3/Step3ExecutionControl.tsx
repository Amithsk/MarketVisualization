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
    maxTradesAllowed,
    executionEnabled,
    candidates,
    candidatesMode,
    generatedAt,
    loading,
    error,
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

  const removeRow = (index: number) => {
    setStocks((prev) => prev.filter((_, i) => i !== index));
  };

  const handleCompute = () => {
    const validStocks = stocks.filter(
      (s) => s.symbol.trim().length > 0
    );
    if (validStocks.length === 0) return;
    computeStep3Candidates(validStocks);
  };

  const handleFreeze = () => {
    if (!snapshot || candidates.length === 0) return;
    freezeStep3Candidates(candidates);
  };

  const isFrozen = candidatesMode === "AUTO" && candidates.length > 0;

  return (
    <div className="space-y-6">
      {snapshot && (
        <div className="rounded border p-4 text-sm">
          <div className="flex justify-between">
            <span>Market Context</span>
            <span>{snapshot.marketContext}</span>
          </div>
          <div className="flex justify-between">
            <span>Allowed Strategies</span>
            <span>
              {allowedStrategies.length
                ? allowedStrategies.join(", ")
                : "NO_TRADE"}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Execution Enabled</span>
            <span
              className={
                executionEnabled
                  ? "text-green-600"
                  : "text-red-600"
              }
            >
              {executionEnabled ? "YES" : "NO"}
            </span>
          </div>
        </div>
      )}

      {/* ================= INPUT SECTION ================= */}
      {!isFrozen && (
        <div className="rounded border p-4 space-y-4">
          {stocks.map((row, index) => (
            <div key={index} className="border p-3 rounded space-y-2">
              <input
                type="text"
                placeholder="Symbol"
                value={row.symbol}
                onChange={(e) =>
                  updateField(index, "symbol", e.target.value.toUpperCase())
                }
                className="border px-2 py-1 text-sm w-32"
              />

              <div className="grid grid-cols-3 gap-2 text-xs">
                <input type="number" placeholder="Avg Value (Cr)"
                  onChange={(e)=>updateField(index,"avgTradedValue20d",Number(e.target.value))} />
                <input type="number" placeholder="ATR %"
                  onChange={(e)=>updateField(index,"atrPct",Number(e.target.value))} />
                <input type="number" placeholder="Gap %"
                  onChange={(e)=>updateField(index,"gapPct",Number(e.target.value))} />
                <input type="number" placeholder="Stock Open"
                  onChange={(e)=>updateField(index,"stockOpen0915",Number(e.target.value))} />
                <input type="number" placeholder="Stock Current"
                  onChange={(e)=>updateField(index,"stockCurrentPrice",Number(e.target.value))} />
                <input type="number" placeholder="Nifty Open"
                  onChange={(e)=>updateField(index,"niftyOpen0915",Number(e.target.value))} />
                <input type="number" placeholder="Nifty Current"
                  onChange={(e)=>updateField(index,"niftyCurrentPrice",Number(e.target.value))} />
              </div>

              <div className="flex gap-4 text-xs">
                <label>
                  <input type="checkbox"
                    onChange={(e)=>updateField(index,"abnormalCandle",e.target.checked)} />
                  Abnormal
                </label>
                <label>
                  <input type="checkbox"
                    onChange={(e)=>updateField(index,"gapHold",e.target.checked)} />
                  Gap Hold
                </label>
                <label>
                  <input type="checkbox"
                    onChange={(e)=>updateField(index,"structureValid",e.target.checked)} />
                  Structure Valid
                </label>
              </div>
            </div>
          ))}

          <div className="flex gap-4">
            <button onClick={addRow} className="text-xs text-blue-600">
              + Add Stock
            </button>
            <button onClick={handleCompute} className="text-xs text-green-600 font-semibold">
              Compute
            </button>
          </div>
        </div>
      )}

      {/* ================= RESULT SECTION ================= */}
      {candidates.length > 0 && (
        <div className="rounded border p-4 space-y-3">
          {candidates.map((c) => {
            const isPass = c.strategyUsed !== "NO_TRADE";

            return (
              <div key={c.symbol} className="border rounded p-3 text-sm">
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

                <div className="text-xs mt-1">
                  Direction: {c.direction}
                </div>

                <div className="text-xs">
                  Strategy: {c.strategyUsed}
                </div>

                <div className="text-xs text-gray-500 mt-1">
                  {c.reason}
                </div>
              </div>
            );
          })}

          {!isFrozen && (
            <button
              onClick={handleFreeze}
              className="text-xs text-purple-600 font-semibold"
            >
              Freeze Candidates
            </button>
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
