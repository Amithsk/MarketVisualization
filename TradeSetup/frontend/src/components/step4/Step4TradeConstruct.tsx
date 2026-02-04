// src/components/step4/Step4TradeConstruct.tsx

import React from "react";

interface Step4TradeConstructProps {
  tradeDate: string;
}

export default function Step4TradeConstruct({
  tradeDate,
}: Step4TradeConstructProps) {
  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Execution Intent for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Candidate selection */}
      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Selected Instrument
        </h3>
        <div className="mt-2 text-sm text-gray-400 italic">
          No candidate selected
        </div>
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
              disabled
              className="mt-1 w-full rounded border px-2 py-1 text-sm bg-gray-100"
              placeholder="e.g. 0.5"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600">
              Entry Price
            </label>
            <input
              type="number"
              disabled
              className="mt-1 w-full rounded border px-2 py-1 text-sm bg-gray-100"
              placeholder="Derived from strategy"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600">
              Stop Loss
            </label>
            <input
              type="number"
              disabled
              className="mt-1 w-full rounded border px-2 py-1 text-sm bg-gray-100"
              placeholder="Required"
            />
          </div>
        </div>
      </div>

      {/* Freeze placeholder */}
      <div className="rounded border border-dashed p-4 text-sm text-gray-500">
        Final trade freeze will lock:
        <ul className="mt-2 list-disc pl-5 space-y-1">
          <li>Instrument</li>
          <li>Direction</li>
          <li>Risk parameters</li>
          <li>Execution intent</li>
        </ul>
      </div>
    </div>
  );
}