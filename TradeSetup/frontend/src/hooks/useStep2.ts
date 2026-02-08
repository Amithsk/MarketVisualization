"use client";

import { useCallback, useState } from "react";
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

export function useStep2(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step2OpenBehaviorSnapshot | null>(null);
  const [mode, setMode] = useState<Step2Mode>("MANUAL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const previewStep2 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step2PreviewResponse =
        await fetchStep2Preview(tradeDate);

      setSnapshot(response.snapshot);
      setMode(response.mode); // ✅ BACKEND DECIDES
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  const freezeStep2 = useCallback(
    async (params: {
      indexOpenBehavior: IndexOpenBehavior;
      earlyVolatility: EarlyVolatility;
      marketParticipation: MarketParticipation;
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
        setMode("AUTO"); // frozen → authoritative
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
