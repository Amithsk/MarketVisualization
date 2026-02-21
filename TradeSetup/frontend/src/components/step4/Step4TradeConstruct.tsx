// src/components/step4/Step4TradeConstruct.tsx
"use client";

import React, { useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type { TradeCandidate } from "@/types/step3.types";
import type {
  Step4PreviewSnapshot,
  Step4PreviewRequest,
  Step4FreezeRequest,
} from "@/types/step4.types";

interface Step4TradeConstructProps {
  tradeDate: TradeDate;
  candidates: TradeCandidate[];

  preview: Step4PreviewSnapshot | null;
  previewLoading: boolean;
  previewError: any;
  generatePreview: (payload: Step4PreviewRequest) => void;

  frozenTrade: any;
  freezeLoading: boolean;
  freezeError: any;
  freezeTrade: (payload: Step4FreezeRequest) => void;
}

export default function Step4TradeConstruct({
  tradeDate,
  candidates,

  preview,
  previewLoading,
  previewError,
  generatePreview,

  frozenTrade,
  freezeLoading,
  freezeError,
  freezeTrade,
}: Step4TradeConstructProps) {
  const [symbol, setSymbol] = useState<string>("");
  const [capital, setCapital] = useState<number>(100000);
  const [riskPercent, setRiskPercent] = useState<number>(0.5);
  const [entryBuffer, setEntryBuffer] = useState<number>(0);
  const [rMultiple, setRMultiple] = useState<number>(2);
  const [rationale, setRationale] = useState<string>("");

  const isFrozen = !!frozenTrade;

  // -------------------------------------------------
  // PREVIEW (snake_case payload)
  // -------------------------------------------------
  const onPreview = () => {
    if (!symbol) return;

    generatePreview({
      trade_date: tradeDate,
      symbol,
      capital,
      risk_percent: riskPercent,
      entry_buffer: entryBuffer,
      r_multiple: rMultiple,
    });
  };

  // -------------------------------------------------
  // FREEZE (snake_case payload)
  // -------------------------------------------------
  const onFreeze = () => {
    if (!preview || preview.trade_status !== "READY") return;

    freezeTrade({
      trade_date: tradeDate,
      symbol,
      capital,
      risk_percent: riskPercent,
      entry_buffer: entryBuffer,
      r_multiple: rMultiple,
      rationale,
    });
  };

  return (
    <div className="space-y-6">
      <div className="text-sm text-gray-500">
        STEP-4 Execution for{" "}
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

      {/* Risk Inputs */}
      <div className="rounded border p-4 space-y-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Risk Configuration
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <input
            type="number"
            disabled={isFrozen}
            value={capital}
            onChange={(e) => setCapital(Number(e.target.value))}
            placeholder="Capital"
            className="rounded border px-2 py-1 text-sm"
          />

          <input
            type="number"
            disabled={isFrozen}
            value={riskPercent}
            onChange={(e) => setRiskPercent(Number(e.target.value))}
            placeholder="Risk %"
            className="rounded border px-2 py-1 text-sm"
          />

          <input
            type="number"
            disabled={isFrozen}
            value={entryBuffer}
            onChange={(e) => setEntryBuffer(Number(e.target.value))}
            placeholder="Entry Buffer"
            className="rounded border px-2 py-1 text-sm"
          />

          <input
            type="number"
            disabled={isFrozen}
            value={rMultiple}
            onChange={(e) => setRMultiple(Number(e.target.value))}
            placeholder="R Multiple"
            className="rounded border px-2 py-1 text-sm"
          />
        </div>

        {!isFrozen && (
          <button
            onClick={onPreview}
            disabled={!symbol || previewLoading}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {previewLoading ? "Generating..." : "Generate Preview"}
          </button>
        )}
      </div>

      {/* Preview Output */}
      {preview && (
        <div className="rounded border p-4 space-y-2 text-sm">
          <div>Direction: {preview.direction}</div>
          <div>Strategy: {preview.strategy_used}</div>
          <div>Entry: {preview.entry_price}</div>
          <div>Stop: {preview.stop_loss}</div>
          <div>Risk/Share: {preview.risk_per_share}</div>
          <div>Quantity: {preview.quantity}</div>
          <div>Target: {preview.target_price}</div>
          <div>
            Status:{" "}
            <span
              className={
                preview.trade_status === "READY"
                  ? "text-green-600"
                  : "text-red-600"
              }
            >
              {preview.trade_status}
            </span>
          </div>
          {preview.block_reason && (
            <div className="text-red-600">
              Reason: {preview.block_reason}
            </div>
          )}
        </div>
      )}

      {/* Rationale */}
      {!isFrozen && (
        <div>
          <input
            type="text"
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            placeholder="Rationale (optional)"
            className="w-full rounded border px-2 py-1 text-sm"
          />
        </div>
      )}

      {/* Freeze */}
      {!isFrozen && preview?.trade_status === "READY" && (
        <button
          onClick={onFreeze}
          disabled={freezeLoading}
          className="rounded bg-red-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          {freezeLoading ? "Freezing..." : "Freeze Final Trade"}
        </button>
      )}

      {freezeError && (
        <div className="text-sm text-red-600">
          {freezeError.message}
        </div>
      )}

      {isFrozen && (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          Trade is frozen and immutable.
        </div>
      )}
    </div>
  );
}
