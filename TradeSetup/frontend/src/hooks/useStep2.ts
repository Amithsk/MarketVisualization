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

type Step2Mode = "AUTO" | "MANUAL";

/**
 * STEP-2 hook
 * Handles preview + freeze lifecycle for market open behavior.
 * AUTO → backend data
 * MANUAL → user input fallback
 */
export function useStep2(tradeDate: TradeDate) {
  const [state, setState] = useState<
    ApiState<Step2OpenBehaviorSnapshot>
  >({
    data: null,
    loading: false,
    error: null,
  });

  const [mode, setMode] = useState<Step2Mode>("AUTO");

  /**
   * Fetch STEP-2 preview snapshot
   */
  const previewStep2 = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: null,
    }));

    try {
      const response: Step2PreviewResponse =
        await fetchStep2Preview(tradeDate);

      setState({
        data: response.snapshot,
        loading: false,
        error: null,
      });

      setMode("AUTO");
    } catch (error: any) {
      // Backend failed → MANUAL mode
      setState({
        data: null,
        loading: false,
        error,
      });

      setMode("MANUAL");
    }
  }, [tradeDate]);

  /**
   * Freeze STEP-2 snapshot
   * Works in both AUTO and MANUAL modes
   */
  const freezeStep2 = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: null,
    }));

    try {
      const response: Step2FrozenResponse =
        await freezeStep2Behavior(tradeDate);

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
    mode,
    isFrozen: state.data?.freezeStatus === "FROZEN",
    tradeAllowed: state.data?.tradeAllowed ?? false,
    loading: state.loading,
    error: state.error,

    previewStep2,
    freezeStep2,
  };
}
