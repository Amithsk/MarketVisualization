// src/hooks/useStep4.ts
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ApiState } from "@/types/common.types";
import type {
  Step4PreviewRequest,
  Step4PreviewResponse,
  Step4ComputeRequest,
  Step4PreviewSnapshot,
  Step4FreezeRequest,
  FrozenTrade,
} from "@/types/step4.types";
import {
  loadStep4Preview,
  computeStep4Trade,
  freezeFinalTrade,
} from "@/services/step4.api";

/**
 * STEP-4 hook
 * Backend is single source of truth.
 * Flow: Preview → Compute → Freeze
 */
export function useStep4() {
  // =====================================================
  // PHASE-1 → CONTEXT STATE
  // =====================================================

  const [contextState, setContextState] =
    useState<ApiState<Step4PreviewResponse>>({
      data: null,
      loading: false,
      error: null,
    });

  // =====================================================
  // PHASE-2 → COMPUTE STATE
  // =====================================================

  const [computeState, setComputeState] =
    useState<ApiState<Step4PreviewSnapshot>>({
      data: null,
      loading: false,
      error: null,
    });

  // =====================================================
  // FREEZE STATE
  // =====================================================

  const [freezeState, setFreezeState] =
    useState<ApiState<FrozenTrade>>({
      data: null,
      loading: false,
      error: null,
    });

  // =====================================================
  // LOAD CONTEXT (PHASE-1)
  // =====================================================

  const loadPreview = useCallback(
    async (payload: Step4PreviewRequest) => {
      setContextState((prev) => ({
        ...prev,
        loading: true,
        error: null,
      }));

      try {
        const response = await loadStep4Preview(payload);

        setContextState({
          data: response,
          loading: false,
          error: null,
        });

        // Reset compute state whenever context reloads
        setComputeState({
          data: null,
          loading: false,
          error: null,
        });
      } catch (error: any) {
        setContextState((prev) => ({
          data: prev.data,
          loading: false,
          error,
        }));
      }
    },
    []
  );

  // =====================================================
  // COMPUTE (PHASE-2)
  // =====================================================

  const computeTrade = useCallback(
    async (payload: Step4ComputeRequest) => {
      setComputeState((prev) => ({
        ...prev,
        loading: true,
        error: null,
      }));

      try {
        const response = await computeStep4Trade(payload);

        setComputeState({
          data: response.preview,
          loading: false,
          error: null,
        });
      } catch (error: any) {
        setComputeState((prev) => ({
          data: prev.data,
          loading: false,
          error,
        }));
      }
    },
    []
  );

  // =====================================================
  // FREEZE
  // =====================================================

  const freezeTrade = useCallback(
    async (payload: Step4FreezeRequest) => {
      setFreezeState((prev) => ({
        ...prev,
        loading: true,
        error: null,
      }));

      try {
        const response = await freezeFinalTrade(payload);

        setFreezeState({
          data: response.trade,
          loading: false,
          error: null,
        });

        // Clear compute state after freeze
        setComputeState({
          data: null,
          loading: false,
          error: null,
        });
      } catch (error: any) {
        setFreezeState((prev) => ({
          data: prev.data,
          loading: false,
          error,
        }));
      }
    },
    []
  );

  // =====================================================
  // MAIN STATE CHANGE DEBUG (NO RENDER SPAM)
  // =====================================================

  const prevRef = useRef<string | null>(null);

  useEffect(() => {
    const snapshot = JSON.stringify({
      contextMode: contextState.data?.mode ?? null,
      candidateCount: contextState.data?.candidates.length ?? 0,
      computeStatus: computeState.data?.trade_status ?? null,
      frozen: !!freezeState.data,
    });

    if (prevRef.current !== snapshot) {
      console.log(
        "%c[STEP4][STATE CHANGE]",
        "color:#22c55e;font-weight:bold",
        {
          contextMode: contextState.data?.mode,
          candidateCount: contextState.data?.candidates.length,
          computeStatus: computeState.data?.trade_status,
          frozen: !!freezeState.data,
        }
      );

      prevRef.current = snapshot;
    }
  }, [contextState.data, computeState.data, freezeState.data]);

  // =====================================================
  // RETURN CONTRACT
  // =====================================================

  return {
    // PHASE-1
    previewContext: contextState.data,
    previewLoading: contextState.loading,
    previewError: contextState.error,
    loadPreview,

    // PHASE-2
    computeResult: computeState.data,
    computeLoading: computeState.loading,
    computeError: computeState.error,
    computeTrade,

    // FREEZE
    frozenTrade: freezeState.data,
    freezeLoading: freezeState.loading,
    freezeError: freezeState.error,
    freezeTrade,
  };
}