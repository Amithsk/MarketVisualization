// src/hooks/useStep3.ts
"use client";


import { useCallback, useState } from "react";
import type { ApiState, TradeDate } from "@/types/common.types";
import type {
  Step3ExecutionSnapshot,
  Step3ExecutionResponse,
} from "@/types/step3.types";
import { fetchStep3Execution } from "@/services/step3.api";

/**
 * STEP-3 hook
 * Read-only execution control & candidate generation.
 */
export function useStep3(tradeDate: TradeDate) {
  const [state, setState] = useState<ApiState<Step3ExecutionSnapshot>>({
    data: null,
    loading: false,
    error: null,
  });

  /**
   * Fetch STEP-3 execution snapshot
   */
  const executeStep3 = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response: Step3ExecutionResponse =
        await fetchStep3Execution(tradeDate);

      setState({
        data: response.snapshot,
        loading: false,
        error: null,
      });
    } catch (error: any) {
      setState({
        data: null,
        loading: false,
        error,
      });
    }
  }, [tradeDate]);

  return {
    snapshot: state.data,
    executionEnabled: state.data?.executionEnabled ?? false,
    candidates: state.data?.candidates ?? [],
    generatedAt: state.data?.generatedAt ?? null,
    loading: state.loading,
    error: state.error,
    executeStep3,
  };
}