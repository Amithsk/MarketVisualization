// frontend/src/services/step2.api.ts

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2PreviewResponse,
  Step2FrozenResponse,
  Step2ComputeResponse,
  Step2CandleInput,
} from "@/types/step2.types";

/**
 * =====================================================
 * STEP-2 Preview
 * =====================================================
 * Backend returns authoritative snapshot.
 */
export async function fetchStep2Preview(
  tradeDate: TradeDate
): Promise<Step2PreviewResponse> {
  const res = await apiClient.post("/step2/preview", {
    trade_date: tradeDate,
  });

  return res.data;
}

/**
 * =====================================================
 * STEP-2 Compute (Option B — Analytical Breakdown)
 * =====================================================
 * Backend calculates:
 *  - IR High / Low / Range / Ratio
 *  - Volatility State
 *  - VWAP Cross Count
 *  - VWAP State
 *  - Range Hold Status
 *  - Derived classifications
 *  - trade_allowed
 *
 * This DOES NOT freeze.
 */
export async function computeStep2Behavior(params: {
  tradeDate: TradeDate;
  candles: Step2CandleInput[];
}): Promise<Step2ComputeResponse> {
  const res = await apiClient.post("/step2/compute", {
    trade_date: params.tradeDate,
    candles: params.candles,
  });

  return res.data;
}

/**
 * =====================================================
 * STEP-2 Freeze
 * =====================================================
 * Frontend sends ONLY:
 *  - raw candles
 *  - reason
 *
 * Backend derives everything and persists snapshot.
 */
export async function freezeStep2Behavior(params: {
  tradeDate: TradeDate;
  candles: Step2CandleInput[];
  reason?: string;
}): Promise<Step2FrozenResponse> {
  const res = await apiClient.post("/step2/freeze", {
    trade_date: params.tradeDate,
    candles: params.candles,
    reason: params.reason ?? null,
  });

  return res.data;
}
