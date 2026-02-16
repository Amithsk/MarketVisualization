// frontend/src/hooks/useStep3.ts
"use client";

import { useCallback, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step3ExecutionSnapshot,
  Step3ExecutionResponse,
} from "@/types/step3.types";
import { fetchStep3Preview } from "@/services/step3.api";

/**
 * STEP-3 Hook — Execution Control & Stock Selection
 *
 * LOCKED RULES:
 * - Backend is the single source of truth
 * - STEP-3A always computed
 * - STEP-3B mode comes ONLY from backend
 * - Frontend does NOT infer AUTO / MANUAL
 */
export function useStep3(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step3ExecutionSnapshot | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  /**
   * Preview STEP-3
   *
   * - Deterministic
   * - Idempotent
   * - Never fails due to missing automation
   */
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

  return {
    snapshot,

    // -------------------------
    // STEP-3A — Index Level
    // -------------------------

    allowedStrategies: snapshot?.allowedStrategies ?? [],
    maxTradesAllowed: snapshot?.maxTradesAllowed ?? 0,
    executionEnabled: snapshot?.executionEnabled ?? false,

    // -------------------------
    // STEP-3B — Stock Funnel
    // -------------------------

    candidatesMode: snapshot?.candidatesMode ?? "MANUAL",
    candidates: snapshot?.candidates ?? [],

    generatedAt: snapshot?.generatedAt ?? null,

    loading,
    error,

    previewStep3,
  };
}
