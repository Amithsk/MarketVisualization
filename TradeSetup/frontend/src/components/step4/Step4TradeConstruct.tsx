// src/components/step4/Step4TradeConstruct.tsx
"use client";

import React, { useState } from "react";
import type { TradeDate } from "@/types/common.types";
import { useStep3 } from "@/hooks/useStep3";
import { useStep4 } from "@/hooks/useStep4";
import type { FinalTradeDirection, ExecutionMode } from "@/types/step4.types";

interface Step4TradeConstructProps {
  tradeDate: TradeDate;
}

export default function Step4TradeConstruct({
  tradeDate,
}: Step4TradeConstructProps) {
  const { candidates } = useStep3(tradeDate);
  const { freezeTrade, loading, error, isFrozen } = useStep4();

  const [symbol, setSymbol] = useState<string>("");
  const [direction, setDirection] = useState<FinalTradeDirection>("LONG");
  const [executionMode] = useState<ExecutionMode>("MARKET");
  const [riskPercent, setRiskPercent] = useState<number>(0.5);
  const [entryPrice, setEntryPrice] = useState<number>(0);
  const [stopLoss, setStopLoss] = useState<number>(0);
  const [quantity, setQuantity] = useState<number>(0);
  const [rationale, setRationale] = useState<string>("");

  const onFreeze = () => {
    freezeTrade({
      tradeDate,
      symbol,
      direction,
      executionMode,
      riskPercent,
      entryPrice,
      stopLoss,
      quantity,
      rationale,
      freezeStatus: "FROZEN",
      frozenAt: new Date().toISOString(),
    });
  };

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Execution Intent for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Candidate selection */}
      <div className="rounded border p-4 space-y-2">
        <h3 className="text-sm font-semibold text-gray-700">
          Selected Instrument
        </h3>

        <select
          disabled={isFrozen}
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="w-full rounded border px-2 py-1 text-sm"
        >
          <option value="">Select candidate</option>
          {candidates.map((c) => (
            <option key={c.symbol} value={c.symbol}>
              {c.symbol} ({c.direction})
            </option>
          ))}
        </select>
      </div>

      {/* Risk definition */}
      <div className="rounded border p-4 space-y-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Risk Definition
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-gray-600">
              Risk per Trade (%)
            </label>
            <input
              type="number"
              disabled={isFrozen}
              value={riskPercent}
              onChange={(e) => setRiskPercent(Number(e.target.value))}
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600">
              Entry Price
            </label>
            <input
              type="number"
              disabled={isFrozen}
              value={entryPrice}
              onChange={(e) => setEntryPrice(Number(e.target.value))}
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600">
              Stop Loss
            </label>
            <input
              type="number"
              disabled={isFrozen}
              value={stopLoss}
              onChange={(e) => setStopLoss(Number(e.target.value))}
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-xs font-medium text-gray-600">
              Quantity
            </label>
            <input
              type="number"
              disabled={isFrozen}
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600">
              Rationale
            </label>
            <input
              type="text"
              disabled={isFrozen}
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {/* Freeze */}
      {!isFrozen ? (
        <button
          onClick={onFreeze}
          disabled={
            loading ||
            !symbol ||
            entryPrice <= 0 ||
            stopLoss <= 0 ||
            quantity <= 0
          }
          className="rounded bg-red-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Freeze Final Trade
        </button>
      ) : (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          Trade is frozen and immutable.
        </div>
      )}
    </div>
  );
}