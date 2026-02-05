// src/components/layout/StepSection.tsx

import React from "react";

export interface StepSectionProps {
  step: number;
  title: string;
  description?: string;
  disabled?: boolean;
  disabledReason?: string; // 🔒 UX guardrail
  children: React.ReactNode;
}

export default function StepSection({
  step,
  title,
  description,
  disabled = false,
  disabledReason,
  children,
}: StepSectionProps) {
  return (
    <section
      className={`relative rounded-lg border p-6 space-y-4 transition ${
        disabled
          ? "bg-gray-50 border-dashed opacity-60 pointer-events-none"
          : "bg-white"
      }`}
    >
      {/* Header */}
      <header className="space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-500">
            STEP {step}
          </span>
          <h2 className="text-lg font-semibold text-gray-800">
            {title}
          </h2>

          {disabled && (
            <span className="ml-2 rounded bg-gray-200 px-2 py-0.5 text-xs text-gray-600">
              Locked
            </span>
          )}
        </div>

        {description && (
          <p className="text-sm text-gray-500">
            {description}
          </p>
        )}
      </header>

      {/* Content */}
      <div>{children}</div>

      {/* Disabled explanation */}
      {disabled && (
        <div className="mt-2 rounded border border-gray-200 bg-gray-100 p-3 text-xs text-gray-600">
          {disabledReason ??
            "Complete the required previous steps to unlock this section."}
        </div>
      )}
    </section>
  );
}
