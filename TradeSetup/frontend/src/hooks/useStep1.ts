//frontend/src/hooks/useStep1.ts
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

type SystemMarketData = {
  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;
};

export function useStep1(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step1ContextSnapshot | null>(null);
  const [mode, setMode] = useState<Step1Mode>("AUTO");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  /**
   * STEP-1 PREVIEW
   * Backend decides AUTO vs MANUAL.
   * Missing data ⇒ MANUAL (never error).
   */
  const previewStep1 = useCallback(async () => {
    console.log("[DEBUG][STEP-1][PREVIEW] request start", {
      tradeDate,
    });

    setLoading(true);
    setError(null);

    try {
      const response: Step1PreviewResponse =
        await fetchStep1Preview(tradeDate);

      console.log(
        "[DEBUG][STEP-1][PREVIEW] response",
        response
      );

      setSnapshot(response.snapshot);
      setMode(response.mode);

      console.log(
        "[DEBUG][STEP-1][PREVIEW] mode set",
        response.mode
      );
    } catch (err) {
      console.error(
        "[DEBUG][STEP-1][PREVIEW] failed → MANUAL fallback",
        err
      );

      setSnapshot(null);
      setMode("MANUAL");
      setError(err);
    } finally {
      setLoading(false);
      console.log("[DEBUG][STEP-1][PREVIEW] request end");
    }
  }, [tradeDate]);

  /**
   * STEP-1 FREEZE
   * Trader submits ALL manual inputs.
   * Backend re-derives + locks snapshot.
   */
  const freezeStep1 = useCallback(
    async (params: {
      marketBias: MarketBias;
      gapContext?: string;
      preOpenPrice?: number;
      premarketNotes?: string;
      systemMarketData?: SystemMarketData;
    }) => {
      console.log("[DEBUG][STEP-1][FREEZE] request start", {
        tradeDate,
        params,
      });

      setLoading(true);
      setError(null);

      try {
        const response: Step1FrozenResponse =
          await freezeStep1Context({
            tradeDate,
            marketBias: params.marketBias,
            gapContext: params.gapContext,
            preOpenPrice: params.preOpenPrice,
            preMarketNotes: params.premarketNotes,
            systemMarketData: params.systemMarketData,
          });

        console.log(
          "[DEBUG][STEP-1][FREEZE] response",
          response
        );

        setSnapshot(response.snapshot);
        setMode("AUTO");

        console.log(
          "[DEBUG][STEP-1][FREEZE] snapshot frozen at",
          response.snapshot?.frozenAt
        );
      } catch (err) {
        console.error(
          "[DEBUG][STEP-1][FREEZE] failed",
          err
        );
        setError(err);
      } finally {
        setLoading(false);
        console.log("[DEBUG][STEP-1][FREEZE] request end");
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
