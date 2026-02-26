// =========================================================
// File: frontend/src/hooks/useStep3.ts
// =========================================================

"use client";

import { useCallback, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step3ExecutionSnapshot,
  Step3ExecutionResponse,
  TradeCandidate,
  Step3StockContext,
} from "@/types/step3.types";

import {
  fetchStep3Preview,
  computeStep3,
  freezeStep3,
} from "@/services/step3.api";

/**
 * STEP-3 Hook — Execution Control & Stock Selection
 * Backend is authoritative.
 * Hook is responsible for normalization.
 */

export function useStep3(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step3ExecutionSnapshot | null>(null);

  const [canFreeze, setCanFreeze] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  // ======================================================
  // 🔥 NORMALIZATION LAYER (snake_case → camelCase)
  // ======================================================

  const normalizeSnapshot = (
    apiSnapshot: any
  ): Step3ExecutionSnapshot => {
    return {
      ...apiSnapshot,

      candidates: (apiSnapshot.candidates || []).map((c: any) => ({
        symbol: c.symbol,
        direction: c.direction,
        strategyUsed: c.strategy_used ?? c.strategyUsed ?? "NO_TRADE",

        // Layer-1
        avgTradedValue20d:
          c.avgTradedValue20d ??
          c.avg_traded_value_20d ??
          0,

        atrPct:
          c.atrPct ??
          c.atr_pct ??
          0,

        abnormalCandle:
          c.abnormalCandle ??
          c.abnormal_candle ??
          false,

        // Structural fields
        rsValue: c.rs_value ?? c.rsValue ?? null,
        gapHigh: c.gap_high ?? c.gapHigh ?? null,
        gapLow: c.gap_low ?? c.gapLow ?? null,
        intradayHigh: c.intraday_high ?? c.intradayHigh ?? null,
        intradayLow: c.intraday_low ?? c.intradayLow ?? null,
        lastHigherLow:
          c.last_higher_low ?? c.lastHigherLow ?? null,
        yesterdayClose:
          c.yesterday_close ?? c.yesterdayClose ?? null,
        vwapValue:
          c.vwap_value ?? c.vwapValue ?? null,

        structureValid:
          c.structure_valid ?? c.structureValid ?? false,

        reason: c.reason,
      })),
    };
  };

  // ======================================================
  // PREVIEW
  // ======================================================

  const previewStep3 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step3ExecutionResponse =
        await fetchStep3Preview(tradeDate);

      const normalized = normalizeSnapshot(response.snapshot);

      setSnapshot(normalized);
      setCanFreeze(response.canFreeze);

    } catch (err) {
      setError(err);
      setSnapshot(null);
      setCanFreeze(false);
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  // ======================================================
  // COMPUTE
  // ======================================================

  const computeStep3Candidates = useCallback(
    async (stocks: Step3StockContext[]) => {
      setLoading(true);
      setError(null);

      try {
        const response: Step3ExecutionResponse =
          await computeStep3(tradeDate, stocks);

        const normalized = normalizeSnapshot(response.snapshot);

        setSnapshot(normalized);
        setCanFreeze(response.canFreeze);

      } catch (err) {
        setError(err);
        setCanFreeze(false);
      } finally {
        setLoading(false);
      }
    },
    [tradeDate]
  );

  // ======================================================
  // FREEZE
  // ======================================================

  const freezeStep3Candidates = useCallback(
    async (candidates: TradeCandidate[]) => {
      setLoading(true);
      setError(null);

      try {
        const response: Step3ExecutionResponse =
          await freezeStep3(tradeDate, candidates);

        const normalized = normalizeSnapshot(response.snapshot);

        setSnapshot(normalized);
        setCanFreeze(response.canFreeze);

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
    canFreeze,

    // STEP-3A
    marketContext: snapshot?.marketContext ?? null,
    tradePermission: snapshot?.tradePermission ?? null,
    allowedStrategies: snapshot?.allowedStrategies ?? [],
    maxTradesAllowed: snapshot?.maxTradesAllowed ?? 0,
    executionEnabled: snapshot?.executionEnabled ?? false,

    // STEP-3B
    candidatesMode: snapshot?.candidatesMode ?? "MANUAL",
    candidates: snapshot?.candidates ?? [],
    generatedAt: snapshot?.generatedAt ?? null,

    previewStep3,
    computeStep3Candidates,
    freezeStep3Candidates,

    loading,
    error,
  };
}