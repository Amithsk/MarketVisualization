// src/hooks/useStep3.ts
"use client";

import { useCallback, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type {
  Step3ExecutionSnapshot,
  Step3ExecutionResponse,
} from "@/types/step3.types";
import { fetchStep3Execution } from "@/services/step3.api";

/**
 * STEP-3 Hook — Execution Control & Candidate Selection
 *
 * Backend is the single source of truth.
 * Frontend does NOT infer AUTO / MANUAL.
 * Frontend only renders backend decisions.
 */
export function useStep3(tradeDate: TradeDate) {
  const [snapshot, setSnapshot] =
    useState<Step3ExecutionSnapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  /**
   * Execute STEP-3
   *
   * - Deterministic
   * - Idempotent
   * - Read-only
   */
  const executeStep3 = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: Step3ExecutionResponse =
        await fetchStep3Execution(tradeDate);

      // Backend response already matches frontend contract
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

    // STEP-3.1 — System gate
    executionEnabled: snapshot?.executionEnabled ?? false,

    // STEP-3.2 — Backend authority
    candidatesMode: snapshot?.candidatesMode ?? "MANUAL",
    candidates: snapshot?.candidates ?? [],

    generatedAt: snapshot?.generatedAt ?? null,

    loading,
    error,

    executeStep3,
  };
}
