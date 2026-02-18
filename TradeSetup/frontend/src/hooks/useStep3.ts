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
 * ARCHITECTURE GUARANTEE
 * ----------------------
 * - Backend is the single source of truth
 * - Preview never mutates
 * - Compute evaluates only (no persist)
 * - Freeze persists deterministic result only
 * - No frontend inference of AUTO / MANUAL
 *
 * Hybrid Mode (Phase-1):
 *   - UI sends full Step3StockContext[]
 *
 * Future Automation:
 *   - UI will stop sending manual metrics
 *   - Backend will construct Step3StockContext internally
 *   - This hook will NOT require modification
 */

export function useStep3(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step3ExecutionSnapshot | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  // ======================================================
  // PREVIEW
  // ======================================================

  const previewStep3 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step3ExecutionResponse =
        await fetchStep3Preview(tradeDate);

      setSnapshot(response.snapshot);
    } catch (err) {
      setError(err);
      setSnapshot(null);
    } finally {
      setLoading(false);
    }
  }, [tradeDate]);

  // ======================================================
  // COMPUTE (Hybrid Manual Input)
  // ======================================================

  const computeStep3Candidates = useCallback(
    async (stocks: Step3StockContext[]) => {
      setLoading(true);
      setError(null);

      try {
        const response: Step3ExecutionResponse =
          await computeStep3(tradeDate, stocks);

        setSnapshot(response.snapshot);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    },
    [tradeDate]
  );

  // ======================================================
  // FREEZE (Persist Final Output Only)
  // ======================================================

  const freezeStep3Candidates = useCallback(
    async (candidates: TradeCandidate[]) => {
      setLoading(true);
      setError(null);

      try {
        const response: Step3ExecutionResponse =
          await freezeStep3(tradeDate, candidates);

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
