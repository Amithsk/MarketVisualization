// src/components/step4/Step4TradePreview.tsx
"use client";

import React from "react";
import type { TradeDate } from "@/types/common.types";
import type { FrozenTrade } from "@/types/step4.types";

interface Step4TradePreviewProps {
  tradeDate: TradeDate;
  trade: FrozenTrade | null;
}

export default function Step4TradePreview({
  tradeDate,
  trade,
}: Step4TradePreviewProps) {
  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Final Frozen Trade for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Trade summary */}
      <div className="rounded border">
        <div className="border-b px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-700">
            Frozen Trade Snapshot
          </h3>
          <p className="text-xs text-gray-500">
            Immutable execution record
          </p>
        </div>

        <div className="p-4 space-y-2">
          {!trade ? (
            <div className="text-sm text-gray-400 italic">
              No frozen trade yet
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
                <span className="text-gray-500">Setup</span>
                <span className="font-medium">{trade.setupType}</span>
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
                <span className="text-gray-500">Risk / Share</span>
                <span className="font-medium">
                  {trade.riskPerShare}
                </span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Quantity</span>
                <span className="font-medium">{trade.quantity}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Target Price</span>
                <span className="font-medium">
                  {trade.targetPrice}
                </span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Risk %</span>
                <span className="font-medium">
                  {trade.riskPercent}%
                </span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Entry Buffer</span>
                <span className="font-medium">
                  {trade.entryBuffer}
                </span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">R Multiple</span>
                <span className="font-medium">
                  {trade.rMultiple}
                </span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Trade Status</span>
                <span
                  className={
                    trade.tradeStatus === "READY"
                      ? "font-medium text-green-600"
                      : "font-medium text-red-600"
                  }
                >
                  {trade.tradeStatus}
                </span>
              </div>

              {trade.blockReason && (
                <div className="text-sm text-red-600">
                  Reason: {trade.blockReason}
                </div>
              )}

              {trade.rationale && (
                <div className="pt-2 text-sm text-gray-600">
                  <span className="font-medium">Rationale:</span>{" "}
                  {trade.rationale}
                </div>
              )}

              <div className="pt-2 text-xs text-gray-400">
                Frozen at: {trade.frozenAt}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Risk context */}
      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Discipline Notes
        </h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-gray-500 space-y-1">
          <li>Execution values are backend-derived</li>
          <li>Position sizing is calculated automatically</li>
          <li>Trade snapshot is immutable once frozen</li>
        </ul>
      </div>
    </div>
  );
}
