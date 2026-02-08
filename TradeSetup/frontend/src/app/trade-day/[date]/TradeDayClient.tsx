"use client";

// frontend/src/app/trade-day/[date]/TradeDayClient.tsx

import StepSection from "@/components/layout/StepSection";

import Step1Context from "@/components/step1/Step1Context";
import Step2OpenBehavior from "@/components/step2/Step2OpenBehavior";
import Step3ExecutionControl from "@/components/step3/Step3ExecutionControl";
import Step4TradePreview from "@/components/step4/Step4TradePreview";
import Step4TradeConstruct from "@/components/step4/Step4TradeConstruct";

import { useTradeDayState } from "@/hooks/useTradeDayState";
import type { TradeDate } from "@/types/common.types";

interface TradeDayClientProps {
  tradeDate: TradeDate;
}

export default function TradeDayClient({
  tradeDate,
}: TradeDayClientProps) {
  const {
    canAccessStep2,
    canAccessStep3,
    canAccessStep4,

    step3,
    step4,
  } = useTradeDayState(tradeDate);

  console.log("[DEBUG][GATE] tradeDate =", tradeDate);
  console.log("[DEBUG][GATE] canAccessStep2 =", canAccessStep2);
  console.log("[DEBUG][GATE] canAccessStep3 =", canAccessStep3);
  console.log("[DEBUG][GATE] canAccessStep4 =", canAccessStep4);

  const { candidates } = step3;

  const {
    trade,
    isFrozen,
    freezeTrade,
    loading: step4Loading,
    error: step4Error,
  } = step4;

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
        disabled={!canAccessStep2}
      >
        {canAccessStep2 && (
          <>
            {console.log(
              "[DEBUG][RENDER] STEP-2 rendered (STEP-1 is frozen)"
            )}
            <Step2OpenBehavior tradeDate={tradeDate} />
          </>
        )}
      </StepSection>

      {/* STEP 3 — Execution Control & Stock Selection */}
      <StepSection
        step={3}
        title="Execution Control & Stock Selection"
        description="System-selected candidates (read-only)"
        disabled={!canAccessStep3}
      >
        {canAccessStep3 && (
          <>
            {console.log(
              "[DEBUG][RENDER] STEP-3 rendered (STEP-2 frozen & trade allowed)"
            )}
            <Step3ExecutionControl tradeDate={tradeDate} />
          </>
        )}
      </StepSection>

      {/* STEP 4 — Trade Construction */}
      <StepSection
        step={4}
        title="Execution & Trade Construction"
        description="Risk, position sizing, and final trade intent"
        disabled={!canAccessStep4}
      >
        {canAccessStep4 && (
          <>
            {console.log(
              "[DEBUG][RENDER] STEP-4 rendered (execution enabled)"
            )}
            <div className="space-y-6">
              <Step4TradePreview
                tradeDate={tradeDate}
                trade={trade}
                isFrozen={isFrozen}
              />

              <Step4TradeConstruct
                tradeDate={tradeDate}
                candidates={candidates}
                freezeTrade={freezeTrade}
                loading={step4Loading}
                error={step4Error}
                isFrozen={isFrozen}
              />
            </div>
          </>
        )}
      </StepSection>
    </main>
  );
}
