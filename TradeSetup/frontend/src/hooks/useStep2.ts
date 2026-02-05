// src/hooks/useStep2.ts
"use client";

import { useCallback, useState } from "react";
import type { ApiState, TradeDate } from "@/types/common.types";
import type {
  Step2OpenBehaviorSnapshot,
  Step2PreviewResponse,
  Step2FrozenResponse,
} from "@/types/step2.types";
import {
  fetchStep2Preview,
  freezeStep2Behavior,
} from "@/services/step2.api";

/**
 * STEP-2 hook
 * Handles preview + freeze lifecycle for market open behavior.
 */
export function useStep2(tradeDate: TradeDate) {
  const [state, setState] = useState<ApiState<Step2OpenBehaviorSnapshot>>({
    data: null,
    loading: false,
    error: null,
  });

  /**
   * Fetch STEP-2 preview snapshot
   */
  const previewStep2 = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response: Step2PreviewResponse = await fetchStep2Preview(tradeDate);
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

  /**
   * Freeze STEP-2 snapshot
   */
  const freezeStep2 = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response: Step2FrozenResponse = await freezeStep2Behavior(tradeDate);
      setState({
        data: response.snapshot,
        loading: false,
        error: null,
      });
    } catch (error: any) {
      setState((prev) => ({
        data: prev.data,
        loading: false,
        error,
      }));
    }
  }, [tradeDate]);

  return {
    snapshot: state.data,
    isFrozen: state.data?.freezeStatus === "FROZEN",
    tradeAllowed: state.data?.tradeAllowed ?? false,
    loading: state.loading,
    error: state.error,
    previewStep2,
    freezeStep2,
  };
}