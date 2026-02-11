
// frontend/src/app/trade-day/[date]/TradeDayClient.tsx"use client";
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

  const { candidates } = step3;
  const { trade, isFrozen, freezeTrade, loading, error } = step4;

  return (
    <main className="max-w-6xl mx-auto px-6 py-6 space-y-8">
      <header>
        <h1 className="text-2xl font-semibold">
          Trade Day — {tradeDate}
        </h1>
      </header>

      <StepSection step={1} title="Pre-Market Context">
        <Step1Context tradeDate={tradeDate} step1={step1} />
      </StepSection>

      <StepSection step={2} title="Market Open Behavior" disabled={!canAccessStep2}>
        {canAccessStep2 && (
          <Step2OpenBehavior tradeDate={tradeDate} step2={step2} />
        )}
      </StepSection>

      <StepSection step={3} title="Execution Control" disabled={!canAccessStep3}>
        {canAccessStep3 && (
          <Step3ExecutionControl tradeDate={tradeDate} step3={step3} />
        )}
      </StepSection>

      <StepSection step={4} title="Trade Construction" disabled={!canAccessStep4}>
        {canAccessStep4 && (
          <>
            <Step4TradePreview
              tradeDate={tradeDate}
              trade={trade}
              isFrozen={isFrozen}
            />
            <Step4TradeConstruct
              tradeDate={tradeDate}
              candidates={candidates}
              freezeTrade={freezeTrade}
              loading={loading}
              error={error}
              isFrozen={isFrozen}
            />
          </>
        )}
      </StepSection>
    </main>
  );
}
