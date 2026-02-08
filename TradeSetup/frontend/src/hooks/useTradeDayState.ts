// src/hooks/useTradeDayState.ts
"use client";

import { useMemo } from "react";
import type { TradeDate } from "@/types/common.types";

import { useStep1 } from "@/hooks/useStep1";
import { useStep2 } from "@/hooks/useStep2";
import { useStep3 } from "@/hooks/useStep3";
import { useStep4 } from "@/hooks/useStep4";

/**
 * Trade Day Orchestrator
 * ---------------------
 * PURE orchestration + gating only.
 *
 * ❌ No API calls
 * ❌ No previews
 * ❌ No execution triggers
 *
 * Each STEP component is responsible for
 * calling its own preview / execute APIs
 * ONLY when it is actually rendered.
 *
 * Backend is the source of truth.
 */
export function useTradeDayState(tradeDate: TradeDate) {
  // Hooks are passive holders of state + actions
  const step1 = useStep1(tradeDate);
  const step2 = useStep2(tradeDate);
  const step3 = useStep3(tradeDate);
  const step4 = useStep4();

  /**
   * Gating logic ONLY
   * No side effects
   */
  const gates = useMemo(() => {
    const step1Frozen = step1.isFrozen;
    const step2Frozen = step2.isFrozen;

    const tradeAllowed = step2.tradeAllowed === true;

    // STEP-3.1 gate (backend decision)
    const executionEnabled = step3.executionEnabled === true;

    // STEP-4 does NOT depend on candidate count
    const tradeFrozen = step4.isFrozen;

    return {
      canAccessStep1: true,

      // STEP-2 unlocked only after STEP-1 freeze
      canAccessStep2: step1Frozen,

      // STEP-3 unlocked only after STEP-2 freeze + trade allowed
      canAccessStep3:
        step1Frozen &&
        step2Frozen &&
        tradeAllowed,

      // STEP-4 unlocked only after execution is enabled
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

    // Expose step hooks (state + actions)
    step1,
    step2,
    step3,
    step4,

    // Gating flags
    ...gates,
  };
}
