// src/hooks/useStep4.ts
"use client";

import { useCallback, useState } from "react";
import type { ApiState } from "@/types/common.types";
import type {
  Step4PreviewRequest,
  Step4PreviewSnapshot,
  Step4FreezeRequest,
  FrozenTrade,
} from "@/types/step4.types";
import {
  generateStep4Preview,
  freezeFinalTrade,
} from "@/services/step4.api";

/**
 * STEP-4 hook
 * Backend is single source of truth.
 */
export function useStep4() {
  const [previewState, setPreviewState] =
    useState<ApiState<Step4PreviewSnapshot>>({
      data: null,
      loading: false,
      error: null,
    });

  const [freezeState, setFreezeState] =
    useState<ApiState<FrozenTrade>>({
      data: null,
      loading: false,
      error: null,
    });

  /**
   * Generate / overwrite preview
   */
  const generatePreview = useCallback(
    async (payload: Step4PreviewRequest) => {
      setPreviewState((prev) => ({
        ...prev,
        loading: true,
        error: null,
      }));

      try {
        const response = await generateStep4Preview(payload);

        setPreviewState({
          data: response.preview,
          loading: false,
          error: null,
        });
      } catch (error: any) {
        setPreviewState((prev) => ({
          data: prev.data,
          loading: false,
          error,
        }));
      }
    },
    []
  );

  /**
   * Freeze trade (irreversible)
   */
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

  return {
    // Preview
    preview: previewState.data,
    previewLoading: previewState.loading,
    previewError: previewState.error,
    generatePreview,

    // Freeze
    frozenTrade: freezeState.data,
    freezeLoading: freezeState.loading,
    freezeError: freezeState.error,
    freezeTrade,
  };
}
