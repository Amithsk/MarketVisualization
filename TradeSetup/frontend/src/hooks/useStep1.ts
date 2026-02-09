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
  const [error, setError] = useState<any>(null);

  console.log("[DEBUG][STEP-1][HOOK][RENDER]", {
    tradeDate,
    mode,
    hasSnapshot: !!snapshot,
    hasDerivedContext: !!derivedContext,
    suggestedMarketContext,
    frozenAt: snapshot?.frozenAt,
    loading,
  });

  /**
   * STEP-1 PREVIEW
   */
  const previewStep1 = useCallback(async () => {
    console.log("[DEBUG][STEP-1][PREVIEW][HOOK] start", {
      tradeDate,
    });

    setLoading(true);
    setError(null);

    try {
      const response: Step1PreviewResponse =
        await fetchStep1Preview(tradeDate);

      console.log("[DEBUG][STEP-1][PREVIEW][HOOK] response", {
        mode: response.mode,
        snapshot: response.snapshot,
      });

      setSnapshot(response.snapshot);
      setMode(response.mode);

      setDerivedContext(null);
      setSuggestedMarketContext(null);

      console.log("[DEBUG][STEP-1][PREVIEW][HOOK] state updated", {
        mode: response.mode,
        frozenAt: response.snapshot?.frozenAt,
      });
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

  /**
   * STEP-1 COMPUTE (MANUAL MODE ONLY)
   */
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
          last5DayRanges:
            systemMarketData.last5DayRanges,
          preOpenPrice:
            systemMarketData.preOpenPrice,
        });

        console.log("[DEBUG][STEP-1][COMPUTE][HOOK] response", response);

        setDerivedContext(response.derivedContext);
        setSuggestedMarketContext(
          response.suggestedMarketContext as MarketBias
        );

        console.log("[DEBUG][STEP-1][COMPUTE][HOOK] state updated", {
          derivedContext: response.derivedContext,
          suggestedMarketContext:
            response.suggestedMarketContext,
        });
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

  /**
   * STEP-1 FREEZE
   */
  const freezeStep1 = useCallback(
    async (params: {
      marketBias: MarketBias;
      gapContext?: string;
      premarketNotes?: string;
    }) => {
      console.log("[DEBUG][STEP-1][FREEZE][HOOK] start", {
        tradeDate,
        params,
        derivedContext,
      });

      setLoading(true);
      setError(null);

      try {
        const response: Step1FrozenResponse =
          await freezeStep1Context({
            tradeDate,
            marketBias: params.marketBias,
            gapContext: params.gapContext,
            preMarketNotes: params.premarketNotes,
          });

        console.log("[DEBUG][STEP-1][FREEZE][HOOK] response", response);

        setSnapshot(response.snapshot);
        setMode("AUTO");

        setDerivedContext(null);
        setSuggestedMarketContext(null);

        console.log(
          "[DEBUG][STEP-1][FREEZE][HOOK] state updated → AUTO",
          {
            frozenAt: response.snapshot.frozenAt,
          }
        );
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
