// frontend/src/hooks/useStep2.ts
"use client";

import { useCallback, useEffect, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2OpenBehaviorSnapshot,
  Step2PreviewResponse,
  Step2FrozenResponse,
  Step2ComputeResponse,
  Step2CandleInput,
} from "@/types/step2.types";
import {
  fetchStep2Preview,
  computeStep2Behavior,
  freezeStep2Behavior,
} from "@/services/step2.api";

interface UseStep2Options {
  enabled?: boolean;
}

const DEBUG = true;

/**
 * STEP-2 Hook
 *
 * Hybrid Manual Mode (Automation Ready)
 *
 * Phase-1:
 *   - avg5mRangePrevDay manually entered from UI
 *
 * Future Automation:
 *   - backend will auto-derive baseline
 *   - this hook will not need structural change
 */
export function useStep2(
  tradeDate: TradeDate,
  options?: UseStep2Options
) {
  const enabled = options?.enabled ?? false;

  const [snapshot, setSnapshot] =
    useState<Step2OpenBehaviorSnapshot | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  /* =====================================================
     PREVIEW
     ===================================================== */
  const previewStep2 = useCallback(async () => {
    if (!enabled) return;

    if (DEBUG) {
      console.log("[STEP2] PREVIEW START", { tradeDate });
    }

    setLoading(true);
    setError(null);

    try {
      const response: Step2PreviewResponse =
        await fetchStep2Preview(tradeDate);

      if (DEBUG) {
        console.log("[STEP2] PREVIEW RESPONSE", response);
      }

      setSnapshot(response.snapshot ?? null);
    } catch (err) {
      console.error("[STEP2] PREVIEW FAILED", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [tradeDate, enabled]);

  useEffect(() => {
    if (!enabled) return;
    if (snapshot) return;

    previewStep2();
  }, [enabled, snapshot, previewStep2]);

  /* =====================================================
     COMPUTE
     ===================================================== */
  const computeStep2 = useCallback(
    async (params: {
      candles: Step2CandleInput[];
      avg5mRangePrevDay: number;
    }) => {
      if (!enabled) return;
      if (snapshot?.frozen_at) return;

      setLoading(true);
      setError(null);

      try {
        const response: Step2ComputeResponse =
          await computeStep2Behavior({
            tradeDate,
            candles: params.candles,
            avg5mRangePrevDay: params.avg5mRangePrevDay,
          });

        if (DEBUG) {
          console.log("[STEP2] COMPUTE SUCCESS", response);
        }

        setSnapshot(response.snapshot);
      } catch (err) {
        console.error("[STEP2] COMPUTE FAILED", err);
        setError(err);
      } finally {
        setLoading(false);
      }
    },
    [tradeDate, enabled, snapshot]
  );

  /* =====================================================
     FREEZE
     ===================================================== */
  const freezeStep2 = useCallback(
    async (params: {
      candles: Step2CandleInput[];
      avg5mRangePrevDay: number;
      reason?: string;
    }) => {
      if (!enabled) return;
      if (snapshot?.frozen_at) return;

      setLoading(true);
      setError(null);

      try {
        const response: Step2FrozenResponse =
          await freezeStep2Behavior({
            tradeDate,
            candles: params.candles,
            avg5mRangePrevDay: params.avg5mRangePrevDay,
            reason: params.reason,
          });

        if (DEBUG) {
          console.log("[STEP2] FREEZE SUCCESS", response);
        }

        setSnapshot(response.snapshot);
      } catch (err) {
        console.error("[STEP2] FREEZE FAILED", err);
        setError(err);
      } finally {
        setLoading(false);
      }
    },
    [tradeDate, enabled, snapshot]
  );

  return {
    snapshot,

    // Backend authoritative derived state
    mode: snapshot?.mode ?? "MANUAL",
    manualInputRequired: snapshot?.manual_input_required ?? true,
    isFrozen: !!snapshot?.frozen_at,
    tradeAllowed: snapshot?.trade_allowed ?? false,

    loading,
    error,

    previewStep2,
    computeStep2,
    freezeStep2,
  };
}
