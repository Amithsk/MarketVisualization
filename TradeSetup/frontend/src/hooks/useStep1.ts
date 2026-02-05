// src/hooks/useStep1.ts
"use client";

import { useCallback, useState } from "react";
import type {
  ApiState,
  ApiMode,
  TradeDate,
} from "@/types/common.types";
import type {
  Step1ContextSnapshot,
  Step1PreviewResponse,
  Step1FrozenResponse,
} from "@/types/step1.types";
import {
  fetchStep1Preview,
  freezeStep1Context,
} from "@/services/step1.api";

/**
 * STEP-1 hook
 * Handles preview + freeze lifecycle for pre-market context.
 * AUTO → backend data
 * MANUAL → user input fallback
 */
export function useStep1(tradeDate: TradeDate) {
  const [state, setState] = useState<ApiState<Step1ContextSnapshot>>({
    data: null,
    loading: false,
    error: null,
    mode: "AUTO", // default assumption
  });

  /**
   * Fetch STEP-1 preview snapshot
   */
  const previewStep1 = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: null,
    }));

    try {
      const response: Step1PreviewResponse =
        await fetchStep1Preview(tradeDate);

      setState({
        data: response.snapshot,
        loading: false,
        error: null,
        mode: "AUTO",
      });
    } catch (error: any) {
      // API failed → switch to MANUAL mode
      setState({
        data: null,
        loading: false,
        error,
        mode: "MANUAL",
      });
    }
  }, [tradeDate]);

  /**
   * Freeze STEP-1 snapshot
   * Works in both AUTO and MANUAL modes
   */
  const freezeStep1 = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: null,
    }));

    try {
      const response: Step1FrozenResponse =
        await freezeStep1Context(tradeDate);

      setState((prev) => ({
        data: response.snapshot,
        loading: false,
        error: null,
        mode: prev.mode, // preserve mode
      }));
    } catch (error: any) {
      setState((prev) => ({
        data: prev.data,
        loading: false,
        error,
        mode: prev.mode,
      }));
    }
  }, [tradeDate]);

  return {
    snapshot: state.data,
    mode: state.mode,
    isFrozen: state.data?.freezeStatus === "FROZEN",
    loading: state.loading,
    error: state.error,

    previewStep1,
    freezeStep1,
  };
}
