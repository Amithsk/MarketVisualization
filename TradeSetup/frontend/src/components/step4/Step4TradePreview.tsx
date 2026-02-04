// src/components/step4/Step4TradePreview.tsx
"use client";

import React from "react";
import { useStep4 } from "@/hooks/useStep4";
import type { TradeDate } from "@/types/common.types";

interface Step4TradePreviewProps {
  tradeDate: TradeDate;
}

export default function Step4TradePreview({
  tradeDate,
}: Step4TradePreviewProps) {
  const { trade, isFrozen } = useStep4();

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Trade Construction Preview for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Warning */}
      {!isFrozen && (
        <div className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          This step finalizes execution intent.  
          Changes after freezing will require explicit review.
        </div>
      )}

      {/* Trade summary */}
      <div className="rounded border">
        <div className="border-b px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-700">
            Trade Summary
          </h3>
          <p className="text-xs text-gray-500">
            Derived from STEP-3 execution control
          </p>
        </div>

        <div className="p-4 space-y-2">
          {!trade ? (
            <div className="text-sm text-gray-400 italic">
              No trade constructed yet
            </div>
          ) : (
            <>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Symbol</span>
                <span className="font-medium">{trade.symbol}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Direction</span>
                <span className="font-medium">{trade.direction}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Execution Mode</span>
                <span className="font-medium">{trade.executionMode}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Entry Price</span>
                <span className="font-medium">{trade.entryPrice}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Stop Loss</span>
                <span className="font-medium">{trade.stopLoss}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Risk %</span>
                <span className="font-medium">
                  {trade.riskPercent}%
                </span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Quantity</span>
                <span className="font-medium">{trade.quantity}</span>
              </div>

              {trade.rationale && (
                <div className="pt-2 text-sm text-gray-600">
                  <span className="font-medium">Rationale:</span>{" "}
                  {trade.rationale}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Risk context */}
      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Risk Context
        </h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-gray-500 space-y-1">
          <li>Risk per trade is explicitly defined</li>
          <li>Position sizing is mandatory</li>
          <li>Stop-loss definition is required</li>
        </ul>
      </div>
    </div>
  );
}