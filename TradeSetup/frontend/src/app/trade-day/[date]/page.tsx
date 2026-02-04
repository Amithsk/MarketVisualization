// frontend/app/trade-day/[date]/page.tsx

import React from "react";
import StepSection from "@/components/layout/StepSection";

// Step components (placeholders for now)
import Step1Context from "@/components/step1/Step1Context";
import Step2OpenBehavior from "@/components/step2/Step2OpenBehavior";
import Step3ExecutionControl from "@/components/step3/Step3ExecutionControl";
import Step4TradePreview from "@/components/step4/Step4TradePreview";

interface TradeDayPageProps {
  params: {
    date: string;
  };
}

export default function TradeDayPage({ params }: TradeDayPageProps) {
  const tradeDate = params.date;

  return (
    <main className="max-w-6xl mx-auto px-6 py-6 space-y-8">
      {/* Header */}
      <header>
        <h1 className="text-2xl font-semibold">
          Trade Day — {tradeDate}
        </h1>
        <p className="text-sm text-gray-500">
          Plan → Observe → Decide → Execute
        </p>
      </header>

      {/* STEP 1 — Pre-Market Context */}
      <StepSection
        step={1}
        title="Pre-Market Context"
        description="Market bias, gap context, and directional preparedness"
      >
        <Step1Context tradeDate={tradeDate} />
      </StepSection>

      {/* STEP 2 — Market Open Behavior */}
      <StepSection
        step={2}
        title="Market Open Behavior"
        description="First reaction, volatility, and confirmation signals"
      >
        <Step2OpenBehavior tradeDate={tradeDate} />
      </StepSection>

      {/* STEP 3 — Execution Control & Stock Selection */}
      <StepSection
        step={3}
        title="Execution Control & Stock Selection"
        description="System-selected candidates (read-only)"
      >
        <Step3ExecutionControl tradeDate={tradeDate} />
      </StepSection>

      {/* STEP 4 — Trade Construction */}
      <StepSection
        step={4}
        title="Execution & Trade Construction"
        description="Risk, position sizing, and final trade intent"
      >
        <Step4TradePreview tradeDate={tradeDate} />
      </StepSection>
    </main>
  );
}