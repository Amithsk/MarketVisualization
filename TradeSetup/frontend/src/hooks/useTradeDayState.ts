// =========================================================
// File: frontend/src/hooks/useTradeDayState.ts
// =========================================================
"use client";

import { useMemo, useRef, useEffect } from "react";
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
 *
 * GATING PRINCIPLE
 * ----------------
 * STEP-4 must unlock ONLY after:
 *  - STEP-1 frozen
 *  - STEP-2 frozen
 *  - STEP-3A execution allowed
 *  - STEP-3B candidates frozen
 */

export function useTradeDayState(tradeDate: TradeDate) {
  // STEP 1
  const step1 = useStep1(tradeDate);

  // STEP 2
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

    const executionEnabled = step3.executionEnabled === true;

    // STEP-3B is considered frozen only when:
    // - Backend declares AUTO mode
    // - Candidates exist
    const step3Frozen =
      step3.candidatesMode === "AUTO" &&
      step3.candidates.length > 0;

    const tradeFrozen = step4.isFrozen;

    return {
      canAccessStep1: true,

      // STEP-2 unlocked only after STEP-1 freeze
      canAccessStep2: step1Frozen,

      // STEP-3 unlocked only after STEP-2 freeze
      canAccessStep3:
        step1Frozen &&
        step2Frozen,

      // STEP-4 unlocked only after:
      // - STEP-3 execution allowed
      // - STEP-3 candidates finalized (frozen)
      // - STEP-4 not already frozen
      canAccessStep4:
        step1Frozen &&
        step2Frozen &&
        executionEnabled &&
        step3Frozen &&
        !tradeFrozen,
    };
  }, [
    step1.isFrozen,
    step2.isFrozen,
    step3.executionEnabled,
    step3.candidatesMode,
    step3.candidates.length,
    step4.isFrozen,
  ]);

  /**
   * Controlled Debug Logging
   */
  const prevGateRef = useRef<string | null>(null);

  useEffect(() => {
    if (!DEBUG) return;

    const snapshot = JSON.stringify(gates);

    if (prevGateRef.current !== snapshot) {
      console.log(
        "%c[GATE STATE]",
        "color:#00aaff;font-weight:bold",
        {
          tradeDate,
          step1Frozen: step1.isFrozen,
          step2Frozen: step2.isFrozen,
          executionEnabled: step3.executionEnabled,
          step3Frozen:
            step3.candidatesMode === "AUTO" &&
            step3.candidates.length > 0,
          canAccessStep2: gates.canAccessStep2,
          canAccessStep3: gates.canAccessStep3,
          canAccessStep4: gates.canAccessStep4,
        }
      );

      prevGateRef.current = snapshot;
    }
  }, [
    gates,
    tradeDate,
    step1.isFrozen,
    step2.isFrozen,
    step3.executionEnabled,
    step3.candidatesMode,
    step3.candidates.length,
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
