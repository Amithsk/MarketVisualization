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
 *
 * Backend is authoritative.
 * Frontend never infers freeze eligibility.
 * candidatesMode reflects persistence state only.
 * canFreeze reflects backend decision.
 *
 * Debug logging only on major state transitions.
 */

export function useStep3(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step3ExecutionSnapshot | null>(null);

  const [canFreeze, setCanFreeze] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  // ======================================================
  // PREVIEW
  // ======================================================

  const previewStep3 = useCallback(async () => {
    console.info("[STEP3][HOOK][PREVIEW][START]", tradeDate);

    setLoading(true);
    setError(null);

    try {
      const response: Step3ExecutionResponse =
        await fetchStep3Preview(tradeDate);

      setSnapshot(response.snapshot);
      setCanFreeze(response.canFreeze);

      console.info(
        "[STEP3][HOOK][PREVIEW][SUCCESS]",
        {
          tradeDate,
          candidatesMode: response.snapshot.candidatesMode,
          executionEnabled: response.snapshot.executionEnabled,
        }
      );
    } catch (err) {
      setError(err);
      setSnapshot(null);
      setCanFreeze(false);

      console.error(
        "[STEP3][HOOK][PREVIEW][ERROR]",
        tradeDate,
        err
      );
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  // ======================================================
  // COMPUTE
  // ======================================================

  const computeStep3Candidates = useCallback(
    async (stocks: Step3StockContext[]) => {
      console.info(
        "[STEP3][HOOK][COMPUTE][START]",
        { tradeDate, stockCount: stocks.length }
      );

      setLoading(true);
      setError(null);

      try {
        const response: Step3ExecutionResponse =
          await computeStep3(tradeDate, stocks);

        setSnapshot(response.snapshot);
        setCanFreeze(response.canFreeze);

        console.info(
          "[STEP3][HOOK][COMPUTE][SUCCESS]",
          {
            tradeDate,
            candidates: response.snapshot.candidates.length,
            canFreeze: response.canFreeze,
          }
        );
      } catch (err) {
        setError(err);
        setCanFreeze(false);

        console.error(
          "[STEP3][HOOK][COMPUTE][ERROR]",
          tradeDate,
          err
        );
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
      console.info(
        "[STEP3][HOOK][FREEZE][START]",
        { tradeDate, candidates: candidates.length }
      );

      setLoading(true);
      setError(null);

      try {
        const response: Step3ExecutionResponse =
          await freezeStep3(tradeDate, candidates);

        setSnapshot(response.snapshot);
        setCanFreeze(response.canFreeze);

        console.info(
          "[STEP3][HOOK][FREEZE][SUCCESS]",
          {
            tradeDate,
            persisted: response.snapshot.candidates.length,
            candidatesMode: response.snapshot.candidatesMode,
          }
        );
      } catch (err) {
        setError(err);

        console.error(
          "[STEP3][HOOK][FREEZE][ERROR]",
          tradeDate,
          err
        );
      } finally {
        setLoading(false);
      }
    },
    [tradeDate]
  );

  return {
    snapshot,
    canFreeze, // 🔥 backend authoritative freeze flag

    // =========================
    // STEP-3A
    // =========================

    marketContext: snapshot?.marketContext ?? null,
    tradePermission: snapshot?.tradePermission ?? null,
    allowedStrategies: snapshot?.allowedStrategies ?? [],
    maxTradesAllowed: snapshot?.maxTradesAllowed ?? 0,
    executionEnabled: snapshot?.executionEnabled ?? false,

    // =========================
    // STEP-3B
    // =========================

    candidatesMode: snapshot?.candidatesMode ?? "MANUAL",
    candidates: snapshot?.candidates ?? [],
    generatedAt: snapshot?.generatedAt ?? null,

    // =========================
    // Actions
    // =========================

    previewStep3,
    computeStep3Candidates,
    freezeStep3Candidates,

    loading,
    error,
  };
}