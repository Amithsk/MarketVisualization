// src/hooks/useStep2.ts
"use client";

import { useCallback, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2OpenBehaviorSnapshot,
  Step2PreviewResponse,
  Step2FrozenResponse,
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";
import {
  fetchStep2Preview,
  freezeStep2Behavior,
} from "@/services/step2.api";

export type Step2Mode = "AUTO" | "MANUAL";

export function useStep2(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step2OpenBehaviorSnapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  /**
   * Mode is DERIVED from snapshot values
   * UNKNOWN → MANUAL
   * Concrete → AUTO
   */
  const mode: Step2Mode =
    snapshot &&
    snapshot.indexOpenBehavior !== "UNKNOWN" &&
    snapshot.earlyVolatility !== "UNKNOWN" &&
    snapshot.marketParticipation !== "UNKNOWN"
      ? "AUTO"
      : "MANUAL";

  /**
   * Preview STEP-2
   * Backend never errors for control flow
   */
  const previewStep2 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step2PreviewResponse =
        await fetchStep2Preview(tradeDate);

      setSnapshot(response.snapshot);
    } catch (err) {
      // Defensive only — should not happen
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  /**
   * Freeze STEP-2
   * Trader submits observed behavior
   */
  const freezeStep2 = useCallback(
    async (params: {
      indexOpenBehavior: IndexOpenBehavior;
      earlyVolatility: EarlyVolatility;
      marketParticipation: MarketParticipation;
      tradeAllowed: boolean;
    }) => {
      setLoading(true);
      setError(null);

      try {
        const response: Step2FrozenResponse =
          await freezeStep2Behavior({
            tradeDate,
            ...params,
          });

        setSnapshot(response.snapshot);
      } catch (err) {
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
