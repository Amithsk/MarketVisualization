"use client";

import { useCallback, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step1ContextSnapshot,
  Step1PreviewResponse,
  Step1FrozenResponse,
  MarketBias,
} from "@/types/step1.types";
import {
  fetchStep1Preview,
  freezeStep1Context,
} from "@/services/step1.api";

export type Step1Mode = "AUTO" | "MANUAL";

export function useStep1(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step1ContextSnapshot | null>(null);
  const [mode, setMode] = useState<Step1Mode>("AUTO");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const previewStep1 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step1PreviewResponse =
        await fetchStep1Preview(tradeDate);

      setSnapshot(response.snapshot);
      setMode("AUTO");
    } catch (err) {
      setSnapshot(null);
      setMode("MANUAL");
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  const freezeStep1 = useCallback(
    async (params: {
      marketBias: MarketBias;
      premarketNotes?: string;
    }) => {
      setLoading(true);
      setError(null);

      try {
        const response: Step1FrozenResponse =
          await freezeStep1Context({
            tradeDate,
            marketBias: params.marketBias,
            preMarketNotes: params.premarketNotes,
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
    loading,
    error,

    previewStep1,
    freezeStep1,
  };
}
