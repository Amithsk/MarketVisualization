// =========================================================
// File: frontend/src/components/step3/Step3ExecutionControl.tsx
// =========================================================
"use client";

import { useEffect, useRef } from "react";
import type { TradeDate } from "@/types/common.types";
import type { useStep3 } from "@/hooks/useStep3";

interface Step3ExecutionControlProps {
  tradeDate: TradeDate;
  step3: ReturnType<typeof useStep3>;
}

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
  } = step3;

  /**
   * Prevent double preview call in React StrictMode
   */
  const hasPreviewed = useRef(false);

  useEffect(() => {
    if (!hasPreviewed.current) {
      previewStep3();
      hasPreviewed.current = true;
    }
  }, [previewStep3]);

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Execution Control for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {loading && (
        <div className="text-sm text-gray-500">
          Generating STEP-3 snapshot…
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {/* ===================================================== */}
      {/* STEP-3A — Strategy & Risk Control                    */}
      {/* ===================================================== */}
      {snapshot && (
        <div className="rounded border">
          <div className="border-b px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-700">
              STEP-3A — Strategy & Risk Control
            </h3>
          </div>

          <div className="p-4 space-y-2 text-sm">
            {/* 🔹 Market Context */}
            <div className="flex justify-between">
              <span className="text-gray-500">Market Context</span>
              <span className="font-medium">
                {snapshot.marketContext}
              </span>
            </div>

            {/* 🔹 Trade Permission */}
            <div className="flex justify-between">
              <span className="text-gray-500">Trade Permission</span>
              <span className="font-medium">
                {snapshot.tradePermission}
              </span>
            </div>

            {/* 🔹 Allowed Strategies */}
            <div className="flex justify-between">
              <span className="text-gray-500">Allowed Strategies</span>
              <span className="font-medium">
                {allowedStrategies.length > 0
                  ? allowedStrategies.join(", ")
                  : "NO_TRADE"}
              </span>
            </div>

            {/* 🔹 Max Trades */}
            <div className="flex justify-between">
              <span className="text-gray-500">Max Trades Allowed</span>
              <span className="font-medium">
                {maxTradesAllowed}
              </span>
            </div>

            {/* 🔹 Execution Enabled */}
            <div className="flex justify-between">
              <span className="text-gray-500">Execution Enabled</span>
              <span
                className={`font-semibold ${
                  executionEnabled
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {executionEnabled ? "YES" : "NO"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ===================================================== */}
      {/* STEP-3B — Stock Selection Funnel                     */}
      {/* ===================================================== */}
      {snapshot && (
        <div className="rounded border">
          <div className="border-b px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-700">
              STEP-3B — Stock Selection Funnel
            </h3>
            <p className="text-xs text-gray-500">
              {candidatesMode === "AUTO"
                ? "System-generated • Read-only"
                : "Manual entry required • Automation unavailable"}
            </p>
          </div>

          <div className="p-4 space-y-3">
            {candidates.length === 0 ? (
              <div className="text-sm text-gray-400 italic">
                {candidatesMode === "AUTO"
                  ? "No candidates generated for today"
                  : "Manual candidate entry UI should be enabled here"}
              </div>
            ) : (
              candidates.map((c) => (
                <div
                  key={c.symbol}
                  className="flex items-center justify-between rounded border px-3 py-2 text-sm"
                >
                  <div>
                    <div className="font-medium">
                      {c.symbol}
                    </div>
                    <div className="text-xs text-gray-500">
                      {c.strategyUsed}
                    </div>
                    <div className="text-xs text-gray-400">
                      {c.reason}
                    </div>
                  </div>

                  <div className="font-semibold">
                    {c.direction}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ===================================================== */}
      {/* Execution Constraints                                 */}
      {/* ===================================================== */}
      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Execution Constraints
        </h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-gray-500 space-y-1">
          <li>Execution permission is system-controlled</li>
          <li>Candidate mode is backend-controlled</li>
          <li>No quantity or risk decisions at this step</li>
        </ul>

        {generatedAt && (
          <div className="mt-3 text-xs text-gray-400">
            Generated at {generatedAt}
          </div>
        )}
      </div>
    </div>
  );
}
