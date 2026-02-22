// =========================================================
// File: src/hooks/useTradeDayState.ts
// =========================================================
"use client";

import { useMemo, useRef, useEffect } from "react";
import type { TradeDate } from "@/types/common.types";

import { useStep1 } from "@/hooks/useStep1";
import { useStep2 } from "@/hooks/useStep2";
import { useStep3 } from "@/hooks/useStep3";
import { useStep4 } from "@/hooks/useStep4";

const DEBUG = true;

export function useTradeDayState(tradeDate: TradeDate) {
  const step1 = useStep1(tradeDate);

  const step2 = useStep2(tradeDate, {
    enabled: step1.isFrozen,
  });

  const step3 = useStep3(tradeDate);

  const step4 = useStep4();

  const gates = useMemo(() => {
    const step1Frozen = step1.isFrozen;
    const step2Frozen = step2.isFrozen;

    const executionEnabled = step3.executionEnabled === true;

    // STEP-3 frozen strictly means persisted (AUTO mode)
    const step3Frozen = step3.candidatesMode === "AUTO";

    const tradeFrozen = !!step4.frozenTrade;

    return {
      canAccessStep1: true,

      canAccessStep2: step1Frozen,

      canAccessStep3:
        step1Frozen &&
        step2Frozen,

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
    step4.frozenTrade,
  ]);

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
          step3Frozen: step3.candidatesMode === "AUTO",
          tradeFrozen: !!step4.frozenTrade,
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
    step4.frozenTrade,
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