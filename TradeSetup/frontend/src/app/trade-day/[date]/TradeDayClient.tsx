// frontend/src/app/trade-day/[date]/TradeDayClient.tsx
"use client";

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
    step1,
    step2,
    step3,
    step4,
    canAccessStep2,
    canAccessStep3,
    canAccessStep4,
  } = useTradeDayState(tradeDate);

  const {
    previewContext,
    previewLoading,
    previewError,
    loadPreview,

    computeResult,
    computeLoading,
    computeError,
    computeTrade,

    frozenTrade,
    freezeLoading,
    freezeError,
    freezeTrade,
  } = step4;

  const isFrozen = !!frozenTrade;

  return (
    <main className="max-w-6xl mx-auto px-6 py-6 space-y-8">
      <header>
        <h1 className="text-2xl font-semibold">
          Trade Day — {tradeDate}
        </h1>
      </header>

      {/* STEP 1 */}
      <StepSection step={1} title="Pre-Market Context">
        <Step1Context tradeDate={tradeDate} step1={step1} />
      </StepSection>

      {/* STEP 2 */}
      <StepSection
        step={2}
        title="Market Open Behavior"
        disabled={!canAccessStep2}
      >
        {canAccessStep2 && (
          <Step2OpenBehavior tradeDate={tradeDate} step2={step2} />
        )}
      </StepSection>

      {/* STEP 3 */}
      <StepSection
        step={3}
        title="Execution Control"
        disabled={!canAccessStep3}
      >
        {canAccessStep3 && (
          <Step3ExecutionControl
            tradeDate={tradeDate}
            step3={step3}
          />
        )}
      </StepSection>

      {/* STEP 4 */}
      <StepSection
        step={4}
        title="Trade Construction"
        disabled={!canAccessStep4}
      >
        {canAccessStep4 && (
          <>
            {/* Frozen snapshot (if exists) */}
            <Step4TradePreview
              tradeDate={tradeDate}
              trade={frozenTrade}
            />

            {/* Construction + Compute + Freeze */}
            {!isFrozen && (
              <Step4TradeConstruct
                tradeDate={tradeDate}

                previewContext={previewContext}
                previewLoading={previewLoading}
                previewError={previewError}
                loadPreview={loadPreview}

                computeResult={computeResult}
                computeLoading={computeLoading}
                computeError={computeError}
                computeTrade={computeTrade}

                frozenTrade={frozenTrade}
                freezeLoading={freezeLoading}
                freezeError={freezeError}
                freezeTrade={freezeTrade}
              />
            )}
          </>
        )}
      </StepSection>
    </main>
  );
}