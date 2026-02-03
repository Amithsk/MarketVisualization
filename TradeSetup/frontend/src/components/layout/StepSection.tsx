// src/components/layout/StepSection.tsx

import React from "react";

interface StepSectionProps {
  step: number;
  title: string;
  description?: string;
  children: React.ReactNode;
}

export default function StepSection({
  step,
  title,
  description,
  children,
}: StepSectionProps) {
  return (
    <section className="border rounded-lg bg-white shadow-sm">
      {/* Header */}
      <header className="border-b px-5 py-4">
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-black text-sm font-semibold text-white">
            {step}
          </span>

          <div>
            <h2 className="text-lg font-semibold">{title}</h2>
            {description && (
              <p className="text-sm text-gray-500">{description}</p>
            )}
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="p-5">{children}</div>
    </section>
  );
}