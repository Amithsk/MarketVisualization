// src/hooks/useTradeDayState.ts
"use client";

import { useMemo } from "react";
import type { TradeDate } from "@/types/common.types";
import { useStep1 } from "@/hooks/useStep1";
import { useStep2 } from "@/hooks/useStep2";
import { useStep3 } from "@/hooks/useStep3";
import { useStep4 } from "@/hooks/useStep4";

/**
 * Aggregates STEP-1 → STEP-4 state and computes gating logic
 * Backend is the source of truth for progression.
 */
export function useTradeDayState(tradeDate: TradeDate) {
  const step1 = useStep1(tradeDate);
  const step2 = useStep2(tradeDate);
  const step3 = useStep3(tradeDate);
  const step4 = useStep4();

  const gates = useMemo(() => {
    const step1Frozen = step1.isFrozen;
    const step2Frozen = step2.isFrozen;

    const tradeAllowed = step2.tradeAllowed === true;

    // STEP-3.1 — backend gate
    const executionEnabled = step3.executionEnabled === true;

    // STEP-4 must NOT depend on candidates count
    // MANUAL candidate entry is valid
    const tradeFrozen = step4.isFrozen;

    return {
      canAccessStep1: true,

      canAccessStep2: step1Frozen,

      canAccessStep3:
        step1Frozen &&
        step2Frozen &&
        tradeAllowed,

      canAccessStep4:
        step1Frozen &&
        step2Frozen &&
        tradeAllowed &&
        executionEnabled &&
        !tradeFrozen,
    };
  }, [
    step1.isFrozen,
    step2.isFrozen,
    step2.tradeAllowed,
    step3.executionEnabled,
    step4.isFrozen,
  ]);

  return {
    tradeDate,

    step1,
    step2,
    step3,
    step4,

    ...gates,
  };
}
