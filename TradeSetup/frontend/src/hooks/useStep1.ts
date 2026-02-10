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
  computeStep1Context,
} from "@/services/step1.api";

export type Step1Mode = "AUTO" | "MANUAL";

/**
 * STRICT system payload
 * This MUST be complete before freeze
 */
type SystemMarketData = {
  yesterdayClose: number;
  yesterdayHigh: number;
  yesterdayLow: number;
  day2High: number;
  day2Low: number;
  last5DayRanges: number[];
  preOpenPrice: number;
};

type DerivedContext = Record<string, number | string>;

export function useStep1(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step1ContextSnapshot | null>(null);
  const [mode, setMode] = useState<Step1Mode>("AUTO");
  const [derivedContext, setDerivedContext] =
    useState<DerivedContext | null>(null);
  const [suggestedMarketContext, setSuggestedMarketContext] =
    useState<MarketBias | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<unknown>(null);

  console.log("[DEBUG][STEP-1][HOOK][RENDER]", {
    tradeDate,
    mode,
    hasSnapshot: !!snapshot,
    hasDerivedContext: !!derivedContext,
    suggestedMarketContext,
    frozenAt: snapshot?.frozenAt,
    loading,
  });

  /* -------------------------------------------------
   * STEP-1 PREVIEW
   * ------------------------------------------------- */
  const previewStep1 = useCallback(async () => {
    console.log("[DEBUG][STEP-1][PREVIEW][HOOK] start", {
      tradeDate,
    });

    setLoading(true);
    setError(null);

    try {
      const response: Step1PreviewResponse =
        await fetchStep1Preview(tradeDate);

      console.log("[DEBUG][STEP-1][PREVIEW][HOOK] response", response);

      setSnapshot(response.snapshot);
      setMode(response.mode);

      // Reset derived state on preview
      setDerivedContext(null);
      setSuggestedMarketContext(null);
    } catch (err) {
      console.error(
        "[DEBUG][STEP-1][PREVIEW][HOOK] failed → MANUAL fallback",
        err
      );
      setSnapshot(null);
      setMode("MANUAL");
      setError(err);
    } finally {
      setLoading(false);
      console.log("[DEBUG][STEP-1][PREVIEW][HOOK] end");
    }
  }, [tradeDate]);

  /* -------------------------------------------------
   * STEP-1 COMPUTE (MANUAL MODE ONLY)
   * ------------------------------------------------- */
  const computeStep1 = useCallback(
    async (systemMarketData: SystemMarketData) => {
      console.log("[DEBUG][STEP-1][COMPUTE][HOOK] start", {
        systemMarketData,
      });

      setLoading(true);
      setError(null);

      try {
        const response = await computeStep1Context({
          yesterdayClose: systemMarketData.yesterdayClose,
          yesterdayHigh: systemMarketData.yesterdayHigh,
          yesterdayLow: systemMarketData.yesterdayLow,
          day2High: systemMarketData.day2High,
          day2Low: systemMarketData.day2Low,
          last5DayRanges: systemMarketData.last5DayRanges,
          preOpenPrice: systemMarketData.preOpenPrice,
        });

        console.log(
          "[DEBUG][STEP-1][COMPUTE][HOOK] response",
          response
        );

        setDerivedContext(response.derivedContext);
        setSuggestedMarketContext(
          response.suggestedMarketContext as MarketBias
        );
      } catch (err) {
        console.error(
          "[DEBUG][STEP-1][COMPUTE][HOOK] failed",
          err
        );
        setError(err);
      } finally {
        setLoading(false);
        console.log("[DEBUG][STEP-1][COMPUTE][HOOK] end");
      }
    },
    []
  );

  /* -------------------------------------------------
   * STEP-1 FREEZE (AUTHORITATIVE SNAPSHOT)
   * ------------------------------------------------- */
  const freezeStep1 = useCallback(
    async (params: {
      marketBias: MarketBias;
      gapContext: string;
      premarketNotes?: string;
      systemMarketData: SystemMarketData;
    }) => {
      console.log("[DEBUG][STEP-1][FREEZE][HOOK] start", {
        tradeDate,
        params,
        derivedContext,
      });

      if (!derivedContext) {
        console.error(
          "[STEP-1][FREEZE][HOOK] blocked — derivedContext missing"
        );
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response: Step1FrozenResponse =
          await freezeStep1Context({
            tradeDate,
            marketBias: params.marketBias,
            gapContext: params.gapContext,
            preMarketNotes: params.premarketNotes,
            preOpenPrice:
              params.systemMarketData.preOpenPrice,
            derivedContext,
          });

        console.log(
          "[DEBUG][STEP-1][FREEZE][HOOK] response",
          response
        );

        setSnapshot(response.snapshot);
        setMode("AUTO");

        // Clear transient state after freeze
        setDerivedContext(null);
        setSuggestedMarketContext(null);
      } catch (err) {
        console.error(
          "[DEBUG][STEP-1][FREEZE][HOOK] failed",
          err
        );
        setError(err);
      } finally {
        setLoading(false);
        console.log("[DEBUG][STEP-1][FREEZE][HOOK] end");
      }
    },
    [tradeDate, derivedContext]
  );

  return {
    snapshot,
    mode,
    derivedContext,
    suggestedMarketContext,
    isFrozen: !!snapshot?.frozenAt,
    loading,
    error,

    previewStep1,
    computeStep1,
    freezeStep1,
  };
}
