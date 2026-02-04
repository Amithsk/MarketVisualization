// src/components/step3/Step3ExecutionControl.tsx

"use client";

import React, { useEffect } from "react";
import { useStep3 } from "@/hooks/useStep3";
import type { TradeDate } from "@/types/common.types";

interface Step3ExecutionControlProps {
  tradeDate: TradeDate;
}

export default function Step3ExecutionControl({
  tradeDate,
}: Step3ExecutionControlProps) {
  const {
    snapshot,
    executionEnabled,
    candidates,
    generatedAt,
    loading,
    error,
    executeStep3,
  } = useStep3(tradeDate);

  // Auto-run STEP-3 when component mounts
  useEffect(() => {
    executeStep3();
  }, [executeStep3]);

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Execution Control for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Preconditions */}
      {!executionEnabled && (
        <div className="rounded border border-dashed p-4 text-sm text-gray-500">
          STEP-3 becomes active only after STEP-1 and STEP-2 are frozen and
          trading is permitted.
        </div>
      )}

      {/* Loading / Error */}
      {loading && (
        <div className="text-sm text-gray-500">
          Generating execution candidates…
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {/* Candidate list */}
      {executionEnabled && (
        <div className="rounded border">
          <div className="border-b px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-700">
              Eligible Trade Candidates
            </h3>
            <p className="text-xs text-gray-500">
              System-generated • Read-only
            </p>
          </div>

          <div className="p-4 space-y-3">
            {candidates.length === 0 ? (
              <div className="text-sm text-gray-400 italic">
                No candidates generated for today
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

      {/* Execution constraints */}
      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Execution Constraints
        </h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-gray-500 space-y-1">
          <li>No discretionary stock additions</li>
          <li>No quantity decisions at this step</li>
          <li>No entry / exit definitions</li>
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