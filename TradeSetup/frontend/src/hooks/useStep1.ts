// frontend/src/hooks/useStep1.ts
"use client";

import { useCallback, useEffect, useState } from "react";
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

function normalizeSnapshot(raw: any): Step1ContextSnapshot {
  return {
    ...raw,
    frozenAt: raw.frozen_at ?? null,
  };
}

export function useStep1(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step1ContextSnapshot | null>(null);
  const [mode, setMode] = useState<Step1Mode>("AUTO");
  const [derivedContext, setDerivedContext] =
    useState<DerivedContext | null>(null);
  const [suggestedMarketContext, setSuggestedMarketContext] =
    useState<MarketBias | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  /* -------------------------------
     STEP-1 PREVIEW
  -------------------------------- */
  const previewStep1 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step1PreviewResponse =
        await fetchStep1Preview(tradeDate);

      setSnapshot((prev) => {
        if (prev?.frozenAt) return prev;

        return response.snapshot
          ? normalizeSnapshot(response.snapshot)
          : null;
      });

      setMode(response.mode);
      setDerivedContext(null);
      setSuggestedMarketContext(null);
    } catch (err) {
      setSnapshot(null);
      setMode("MANUAL");

      if (err instanceof Error) {
        setError(err);
      } else {
        setError(new Error("Unknown preview error"));
      }
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  useEffect(() => {
    previewStep1();
  }, [previewStep1]);

  /* -------------------------------
     STEP-1 COMPUTE
  -------------------------------- */
  const computeStep1 = useCallback(
    async (systemMarketData: SystemMarketData) => {
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

        setDerivedContext(response.derivedContext);
        setSuggestedMarketContext(
          response.suggestedMarketContext as MarketBias
        );
      } catch (err) {
        if (err instanceof Error) {
          setError(err);
        } else {
          setError(new Error("Unknown compute error"));
        }
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /* -------------------------------
     STEP-1 FREEZE
  -------------------------------- */
  const freezeStep1 = useCallback(
    async (params: {
      marketBias: MarketBias;
      gapContext: string;
      premarketNotes?: string;
      systemMarketData: SystemMarketData;
    }) => {
      if (!derivedContext) return;

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

        setSnapshot(normalizeSnapshot(response.snapshot));
        setMode("AUTO");
        setDerivedContext(null);
        setSuggestedMarketContext(null);
      } catch (err) {
        if (err instanceof Error) {
          setError(err);
        } else {
          setError(new Error("Unknown freeze error"));
        }
      } finally {
        setLoading(false);
      }
    },
    [tradeDate, derivedContext]
  );

  return {
    snapshot,
    mode,
    derivedContext,
    suggestedMarketContext,
    isFrozen: Boolean(snapshot?.frozenAt),
    loading,
    error,
    previewStep1,
    computeStep1,
    freezeStep1,
  };
}
