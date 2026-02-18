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
 * STEP-2 Compute (Hybrid Manual Baseline Support)
 * =====================================================
 *
 * Phase-1:
 *  - avg5mRangePrevDay manually supplied by UI
 *
 * Future Automation:
 *  - backend will auto-derive baseline internally
 *  - frontend will stop sending this field
 */
export async function computeStep2Behavior(params: {
  tradeDate: TradeDate;
  candles: Step2CandleInput[];
  avg5mRangePrevDay: number;
}): Promise<Step2ComputeResponse> {
  const res = await apiClient.post("/step2/compute", {
    trade_date: params.tradeDate,
    candles: params.candles,
    avg_5m_range_prev_day: params.avg5mRangePrevDay,
  });

  return res.data;
}

/**
 * =====================================================
 * STEP-2 Freeze
 * =====================================================
 *
 * Frontend sends:
 *  - raw candles
 *  - avg5mRangePrevDay (manual baseline in hybrid mode)
 *  - reason
 *
 * Backend derives everything and persists snapshot.
 */
export async function freezeStep2Behavior(params: {
  tradeDate: TradeDate;
  candles: Step2CandleInput[];
  avg5mRangePrevDay: number;
  reason?: string;
}): Promise<Step2FrozenResponse> {
  const res = await apiClient.post("/step2/freeze", {
    trade_date: params.tradeDate,
    candles: params.candles,
    avg_5m_range_prev_day: params.avg5mRangePrevDay,
    reason: params.reason ?? null,
  });

  return res.data;
}
