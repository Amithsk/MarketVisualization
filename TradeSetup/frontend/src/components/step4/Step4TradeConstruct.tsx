// src/components/step4/Step4TradeConstruct.tsx
"use client";

import React, { useEffect, useState, useRef } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step4ExecutionBlueprint,
  Step4ComputeRequest,
  Step4FreezeRequest,
  Step4PreviewSnapshot,
} from "@/types/step4.types";

interface Step4TradeConstructProps {
  tradeDate: TradeDate;

  previewContext: {
    mode: "AUTO" | "MANUAL_REQUIRED";
    candidates: Step4ExecutionBlueprint[];
  } | null;
  previewLoading: boolean;
  previewError: any;
  loadPreview: (payload: { trade_date: TradeDate }) => void;

  computeResult: Step4PreviewSnapshot | null;
  computeLoading: boolean;
  computeError: any;
  computeTrade: (payload: Step4ComputeRequest) => void;

  frozenTrade: any;
  freezeLoading: boolean;
  freezeError: any;
  freezeTrade: (payload: Step4FreezeRequest) => void;
}

export default function Step4TradeConstruct({
  tradeDate,
  previewContext,
  previewLoading,
  previewError,
  loadPreview,
  computeResult,
  computeLoading,
  computeError,
  computeTrade,
  frozenTrade,
  freezeLoading,
  freezeError,
  freezeTrade,
}: Step4TradeConstructProps) {
  const [selectedSymbol, setSelectedSymbol] = useState<string>("");
  const [capital, setCapital] = useState<number>(100000);
  const [riskPercent, setRiskPercent] = useState<number>(1);
  const [entryBuffer, setEntryBuffer] = useState<number>(0);
  const [rMultiple, setRMultiple] = useState<number>(2);
  const [rationale, setRationale] = useState<string>("");

  const isFrozen = !!frozenTrade;

  const didLoadRef = useRef<string | null>(null);

  useEffect(() => {
    if (didLoadRef.current === tradeDate) return;
    didLoadRef.current = tradeDate;
    loadPreview({ trade_date: tradeDate });
  }, [tradeDate, loadPreview]);

  const onCompute = () => {
    if (!selectedSymbol) return;

    computeTrade({
      trade_date: tradeDate,
      symbol: selectedSymbol,
      capital,
      risk_percent: riskPercent,
      entry_buffer: entryBuffer,
      r_multiple: rMultiple,
    });
  };

  const onFreeze = () => {
    if (!computeResult || computeResult.trade_status !== "READY") return;

    freezeTrade({
      trade_date: tradeDate,
      symbol: selectedSymbol,
      capital,
      risk_percent: riskPercent,
      entry_buffer: entryBuffer,
      r_multiple: rMultiple,
      rationale,
    });
  };

  return (
    <div className="space-y-8">
      <div className="text-sm text-gray-500">
        STEP-4 Execution Panel —{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* ===============================
         EXECUTION CONTEXT
      =============================== */}
      <div className="rounded border bg-gray-50 p-4">
        <div className="mb-3 text-sm font-semibold text-gray-700">
          Approved Execution Candidates
        </div>

        {previewLoading && (
          <div className="text-sm text-gray-400">
            Loading execution context...
          </div>
        )}

        {previewContext?.mode === "AUTO" &&
          previewContext.candidates.map((c) => (
            <details key={c.symbol} className="mb-3 rounded border bg-white p-4 text-sm">
              <summary className="cursor-pointer font-medium">
                {c.symbol} — {c.direction} ({c.strategy_used})
              </summary>

              <div className="mt-3 grid grid-cols-2 gap-2 text-gray-600">
                <div>Gap High: {c.gap_high ?? "-"}</div>
                <div>Gap Low: {c.gap_low ?? "-"}</div>
                <div>Intraday High: {c.intraday_high ?? "-"}</div>
                <div>Last Higher Low: {c.last_higher_low ?? "-"}</div>
                <div>VWAP: {c.vwap_value ?? "-"}</div>
                <div>
                  Structure Valid:{" "}
                  {c.structure_valid ? "YES" : "NO"}
                </div>
              </div>

              <button
                disabled={isFrozen}
                onClick={() => setSelectedSymbol(c.symbol)}
                className="mt-4 rounded bg-gray-800 px-4 py-1 text-xs text-white"
              >
                Select for Execution
              </button>
            </details>
          ))}

        {previewContext?.mode === "MANUAL_REQUIRED" && (
          <div className="text-sm text-yellow-600">
            No execution candidates available.
          </div>
        )}
      </div>

      {/* ===============================
         RISK CONFIGURATION PANEL
      =============================== */}
      {selectedSymbol && (
        <div className="rounded border bg-white p-6 shadow-sm space-y-6">
          <div className="text-sm font-semibold text-gray-700">
            Execution Parameters — {selectedSymbol}
          </div>

          <div className="grid gap-6 md:grid-cols-4">
            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-500">
                Account Capital (₹)
              </label>
              <input
                type="number"
                disabled={isFrozen}
                value={capital}
                onChange={(e) => setCapital(Number(e.target.value))}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-500">
                Risk % Per Trade
              </label>
              <input
                type="number"
                disabled={isFrozen}
                value={riskPercent}
                onChange={(e) => setRiskPercent(Number(e.target.value))}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-500">
                Entry Buffer
              </label>
              <input
                type="number"
                disabled={isFrozen}
                value={entryBuffer}
                onChange={(e) => setEntryBuffer(Number(e.target.value))}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-500">
                Target R Multiple
              </label>
              <input
                type="number"
                disabled={isFrozen}
                value={rMultiple}
                onChange={(e) => setRMultiple(Number(e.target.value))}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>
          </div>

          {!isFrozen && (
            <button
              onClick={onCompute}
              disabled={computeLoading}
              className="rounded bg-blue-600 px-6 py-2 text-sm text-white disabled:opacity-50"
            >
              {computeLoading ? "Calculating..." : "Calculate Position"}
            </button>
          )}
        </div>
      )}

      {/* ===============================
         COMPUTE RESULT PANEL
      =============================== */}
      {computeResult && (
        <div className="rounded border bg-gray-50 p-6 text-sm space-y-3">
          <div className="font-semibold text-gray-700">
            Position Sizing Output
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>Entry Price: {computeResult.entry_price}</div>
            <div>Stop Loss: {computeResult.stop_loss}</div>
            <div>Risk / Share: {computeResult.risk_per_share}</div>
            <div>Quantity: {computeResult.quantity}</div>
            <div>Target Price: {computeResult.target_price}</div>
            <div>Status: {computeResult.trade_status}</div>
          </div>

          {computeResult.block_reason && (
            <div className="text-red-600">
              Block Reason: {computeResult.block_reason}
            </div>
          )}
        </div>
      )}

      {/* ===============================
         FREEZE PANEL
      =============================== */}
      {!isFrozen && computeResult?.trade_status === "READY" && (
        <div className="space-y-4">
          <input
            type="text"
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            placeholder="Execution rationale (optional)"
            className="w-full rounded border px-3 py-2 text-sm"
          />

          <button
            onClick={onFreeze}
            disabled={freezeLoading}
            className="rounded bg-red-600 px-6 py-2 text-sm text-white disabled:opacity-50"
          >
            {freezeLoading ? "Freezing..." : "Freeze Trade"}
          </button>
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