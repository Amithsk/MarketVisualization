// src/components/step4/Step4TradePreview.tsx

import React from "react";

interface Step4TradePreviewProps {
  tradeDate: string;
}

export default function Step4TradePreview({
  tradeDate,
}: Step4TradePreviewProps) {
  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Trade Construction Preview for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Warning */}
      <div className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        This step finalizes execution intent.  
        Changes after freezing will require explicit review.
      </div>

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

        <div className="p-4">
          <div className="text-sm text-gray-400 italic">
            No trade constructed yet
          </div>
        </div>
      </div>

      {/* Risk context */}
      <div className="rounded border p-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Risk Context
        </h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-gray-500 space-y-1">
          <li>Risk per trade will be explicitly defined</li>
          <li>Position sizing is mandatory</li>
          <li>Stop-loss definition is required</li>
        </ul>
      </div>
    </div>
  );
}