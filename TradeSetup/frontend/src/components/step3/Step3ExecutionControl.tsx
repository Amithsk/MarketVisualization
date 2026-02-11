// src/components/step3/Step3ExecutionControl.tsx
"use client";

import { useEffect } from "react";
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
    executionEnabled,
    candidates,
    candidatesMode,
    generatedAt,
    loading,
    error,
    executeStep3,
  } = step3;

  // Run STEP-3 only when execution is enabled
  useEffect(() => {
    if (!executionEnabled) return;
    executeStep3();
  }, [executionEnabled, executeStep3]);

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Execution Control for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {!executionEnabled && (
        <div className="rounded border border-dashed p-4 text-sm text-gray-500">
          STEP-3 becomes active only after STEP-1 and STEP-2 are frozen and
          trading is permitted.
        </div>
      )}

      {loading && (
        <div className="text-sm text-gray-500">
          Generating execution control…
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {executionEnabled && snapshot && (
        <div className="rounded border">
          <div className="border-b px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-700">
              Trade Candidates
            </h3>
            <p className="text-xs text-gray-500">
              {candidatesMode === "AUTO"
                ? "System-generated • Read-only"
                : "Manual entry required • No automation available"}
            </p>
          </div>

          <div className="p-4 space-y-3">
            {candidates.length === 0 ? (
              <div className="text-sm text-gray-400 italic">
                {candidatesMode === "AUTO"
                  ? "No candidates generated for today"
                  : "Please add trade candidates manually"}
              </div>
            ) : (
              candidates.map((c) => (
                <div
                  key={c.symbol}
                  className="flex items-center justify-between rounded border px-3 py-2 text-sm"
                >
                  <div>
                    <div className="font-medium">{c.symbol}</div>
                    <div className="text-xs text-gray-500">
                      {c.setupType}
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

      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Execution Constraints
        </h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-gray-500 space-y-1">
          <li>Execution permission is system-controlled</li>
          <li>Candidate automation may or may not be available</li>
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
