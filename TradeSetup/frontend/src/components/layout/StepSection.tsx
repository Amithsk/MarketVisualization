// src/components/layout/StepSection.tsx

import React from "react";

export interface StepSectionProps {
  step: number;
  title: string;
  description?: string;
  disabled?: boolean;
  children: React.ReactNode;
}

export default function StepSection({
  step,
  title,
  description,
  disabled = false,
  children,
}: StepSectionProps) {
  return (
    <section
      className={`rounded-lg border p-6 space-y-4 ${
        disabled ? "opacity-50 pointer-events-none" : ""
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
        </div>

        {description && (
          <p className="text-sm text-gray-500">
            {description}
          </p>
        )}
      </header>

      {/* Content */}
      <div>{children}</div>

      {/* Disabled hint */}
      {disabled && (
        <div className="mt-2 text-xs text-gray-400 italic">
          Complete previous steps to unlock this section.
        </div>
      )}
    </section>
  );
}