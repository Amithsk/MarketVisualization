// src/components/step3/Step3ExecutionControl.tsx

import React from "react";

interface Step3ExecutionControlProps {
  tradeDate: string;
}

export default function Step3ExecutionControl({
  tradeDate,
}: Step3ExecutionControlProps) {
  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="text-sm text-gray-500">
        Execution Control for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* Preconditions */}
      <div className="rounded border border-dashed p-4 text-sm text-gray-500">
        STEP-3 becomes active only after STEP-1 and STEP-2 are frozen.  
        Stock selection is system-generated and cannot be modified.
      </div>

      {/* Candidate list */}
      <div className="rounded border">
        <div className="border-b px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-700">
            Eligible Trade Candidates
          </h3>
          <p className="text-xs text-gray-500">
            Generated based on predefined rules and market conditions
          </p>
        </div>

        <div className="p-4">
          <div className="text-sm text-gray-400 italic">
            No candidates generated yet
          </div>
        </div>
      </div>

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
      </div>
    </div>
  );
}