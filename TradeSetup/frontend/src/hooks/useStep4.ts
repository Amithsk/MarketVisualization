// src/hooks/useStep4.ts
"use client";

import { useCallback, useState } from "react";
import type { ApiState } from "@/types/common.types";
import type {
  TradeIntent,
  FrozenTrade,
  Step4FrozenTradeResponse,
} from "@/types/step4.types";
import { freezeFinalTrade } from "@/services/step4.api";

/**
 * STEP-4 hook
 * Handles final trade construction & irreversible freeze.
 */
export function useStep4() {
  const [state, setState] = useState<ApiState<FrozenTrade>>({
    data: null,
    loading: false,
    error: null,
  });

  /**
   * Freeze final trade (irreversible)
   */
  const freezeTrade = useCallback(
    async (tradeIntent: TradeIntent) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const response: Step4FrozenTradeResponse =
          await freezeFinalTrade(tradeIntent);

        setState({
          data: response.trade,
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
    },
    []
  );

  return {
    trade: state.data,
    isFrozen: state.data?.freezeStatus === "FROZEN",
    loading: state.loading,
    error: state.error,
    freezeTrade,
  };
}
