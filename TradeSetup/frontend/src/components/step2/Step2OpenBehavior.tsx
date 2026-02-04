// src/components/step2/Step2OpenBehavior.tsx

import React from "react";

interface Step2OpenBehaviorProps {
  tradeDate: string;
}

export default function Step2OpenBehavior({
  tradeDate,
}: Step2OpenBehaviorProps) {
  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Market Open Behavior for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Observation grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Index Open */}
        <div className="rounded border p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Index Open
          </h3>
          <div className="mt-2 text-sm text-gray-400 italic">
            Not captured yet
          </div>
        </div>

        {/* Volatility / Range */}
        <div className="rounded border p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Early Volatility
          </h3>
          <div className="mt-2 text-sm text-gray-400 italic">
            Not evaluated yet
          </div>
        </div>

        {/* Market Participation */}
        <div className="rounded border p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Market Participation
          </h3>
          <div className="mt-2 text-sm text-gray-400 italic">
            Not evaluated yet
          </div>
        </div>
      </div>

      {/* Trade permission */}
      <div className="rounded border border-dashed p-4">
        <div className="text-sm font-medium text-gray-700">
          Trade Permission
        </div>
        <div className="mt-2 text-sm text-gray-500 italic">
          Trading is not permitted until STEP-2 is evaluated and frozen.
        </div>
      </div>
    </div>
  );
}