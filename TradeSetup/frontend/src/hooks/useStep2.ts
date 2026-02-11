//frontend/src/hooks/useStep2.ts
"use client";

import { useCallback, useEffect, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2OpenBehaviorSnapshot,
  Step2PreviewResponse,
  Step2FrozenResponse,
  Step2Mode,
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";
import {
  fetchStep2Preview,
  freezeStep2Behavior,
} from "@/services/step2.api";

interface UseStep2Options {
  enabled?: boolean; // ← make optional (safe)
}

const DEBUG = true;

export function useStep2(
  tradeDate: TradeDate,
  options?: UseStep2Options
) {
  const enabled = options?.enabled ?? false;

  const [snapshot, setSnapshot] =
    useState<Step2OpenBehaviorSnapshot | null>(null);
  const [mode, setMode] = useState<Step2Mode>("MANUAL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const previewStep2 = useCallback(async () => {
    if (DEBUG)
      console.log(
        "%c[STEP2] PREVIEW START",
        "color:#00cc66;font-weight:bold",
        { tradeDate }
      );

    setLoading(true);
    setError(null);

    try {
      const response: Step2PreviewResponse =
        await fetchStep2Preview(tradeDate);

      if (DEBUG)
        console.log(
          "%c[STEP2] PREVIEW RESPONSE",
          "color:#00cc66",
          response
        );

      setSnapshot(response.snapshot);
      setMode(response.mode);
    } catch (err) {
      console.error("[STEP2] PREVIEW FAILED", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  /**
   * 🔑 Deterministic trigger
   */
  useEffect(() => {
    if (!enabled) return;
    if (snapshot) return;

    if (DEBUG)
      console.log(
        "%c[STEP2] PREVIEW TRIGGERED",
        "color:#00cc66;font-weight:bold"
      );

    previewStep2();
  }, [enabled, snapshot, previewStep2]);

  /**
   * Debug state updates (after React commit)
   */
  useEffect(() => {
    if (!DEBUG) return;

    console.log(
      "%c[STEP2 STATE UPDATE]",
      "color:#00aa55",
      {
        enabled,
        mode,
        frozenAt: snapshot?.frozenAt ?? null,
        tradeAllowed: snapshot?.tradeAllowed ?? null,
      }
    );
  }, [enabled, mode, snapshot]);

  const freezeStep2 = useCallback(
    async (params: {
      indexOpenBehavior: IndexOpenBehavior;
      earlyVolatility: EarlyVolatility;
      marketParticipation: MarketParticipation;
    }) => {
      if (DEBUG)
        console.log(
          "%c[STEP2] FREEZE START",
          "color:#ff8800;font-weight:bold"
        );

      setLoading(true);
      setError(null);

      try {
        const response: Step2FrozenResponse =
          await freezeStep2Behavior({
            tradeDate,
            ...params,
          });

        if (DEBUG)
          console.log(
            "%c[STEP2] FREEZE SUCCESS",
            "color:#ff8800",
            response
          );

        setSnapshot(response.snapshot);
        setMode("AUTO");
      } catch (err) {
        console.error("[STEP2] FREEZE FAILED", err);
        setError(err);
      } finally {
        setLoading(false);
      }
    },
    [tradeDate]
  );

  return {
    snapshot,
    mode,
    isFrozen: !!snapshot?.frozenAt,
    tradeAllowed: snapshot?.tradeAllowed ?? false,
    loading,
    error,
    previewStep2,
    freezeStep2,
  };
}
