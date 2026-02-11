// src/hooks/useTradeDayState.ts
"use client";

import { useMemo } from "react";
import type { TradeDate } from "@/types/common.types";

import { useStep1 } from "@/hooks/useStep1";
import { useStep2 } from "@/hooks/useStep2";
import { useStep3 } from "@/hooks/useStep3";
import { useStep4 } from "@/hooks/useStep4";

const DEBUG = true;

/**
 * Trade Day Orchestrator
 * ---------------------
 * PURE orchestration + gating only.
 *
 * ❌ No API calls
 * ❌ No previews triggered here
 * ❌ No execution logic
 *
 * Backend remains source of truth.
 */
export function useTradeDayState(tradeDate: TradeDate) {
  // STEP 1
  const step1 = useStep1(tradeDate);

  // STEP 2 receives enabled flag from STEP-1 freeze state
  const step2 = useStep2(tradeDate, {
    enabled: step1.isFrozen,
  });

  // STEP 3
  const step3 = useStep3(tradeDate);

  // STEP 4
  const step4 = useStep4();

  /**
   * Gating logic ONLY
   */
  const gates = useMemo(() => {
    const step1Frozen = step1.isFrozen;
    const step2Frozen = step2.isFrozen;
    const tradeAllowed = step2.tradeAllowed === true;
    const executionEnabled = step3.executionEnabled === true;
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

  if (DEBUG) {
    console.log(
      "%c[GATE STATE]",
      "color:#00aaff;font-weight:bold",
      {
        tradeDate,
        step1Frozen: step1.isFrozen,
        step2Frozen: step2.isFrozen,
        tradeAllowed: step2.tradeAllowed,
        executionEnabled: step3.executionEnabled,
        canAccessStep2: gates.canAccessStep2,
        canAccessStep3: gates.canAccessStep3,
        canAccessStep4: gates.canAccessStep4,
      }
    );
  }

  return {
    tradeDate,
    step1,
    step2,
    step3,
    step4,
    ...gates,
  };
}
