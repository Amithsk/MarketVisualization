// src/components/step1/Step1Context.tsx

import React from "react";

interface Step1ContextProps {
  tradeDate: string;
}

export default function Step1Context({ tradeDate }: Step1ContextProps) {
  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Pre-Market Context for <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Snapshot grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Market Bias */}
        <div className="rounded border p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Market Bias
          </h3>
          <div className="mt-2 text-gray-400 text-sm italic">
            Not evaluated yet
          </div>
        </div>

        {/* Gap Context */}
        <div className="rounded border p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Gap Context
          </h3>
          <div className="mt-2 text-gray-400 text-sm italic">
            Not evaluated yet
          </div>
        </div>

        {/* Pre-Market Notes */}
        <div className="rounded border p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Pre-Market Notes
          </h3>
          <div className="mt-2 text-gray-400 text-sm italic">
            No notes added
          </div>
        </div>
      </div>

      {/* Freeze placeholder */}
      <div className="rounded border border-dashed p-4 text-sm text-gray-500">
        STEP-1 will be frozen before market open.  
        Once frozen, this context becomes read-only for the rest of the day.
      </div>
    </div>
  );
}