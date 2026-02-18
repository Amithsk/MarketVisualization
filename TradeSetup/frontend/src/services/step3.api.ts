// =========================================================
// File: frontend/src/services/step3.api.ts
// =========================================================

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step3ExecutionResponse,
  Step3ExecutionSnapshot,
  TradeCandidate,
  Step3StockContext,
} from "@/types/step3.types";

/**
 * Normalize backend snapshot → frontend format
 */
function normalizeSnapshot(raw: any): Step3ExecutionSnapshot {
  return {
    tradeDate: raw.trade_date,

    marketContext: raw.market_context,
    tradePermission: raw.trade_permission,
    allowedStrategies: raw.allowed_strategies ?? [],
    maxTradesAllowed: raw.max_trades_allowed,
    executionEnabled: raw.execution_enabled,

    candidatesMode: raw.candidates_mode,
    candidates:
      raw.candidates?.map((c: any) => ({
        symbol: c.symbol,
        direction: c.direction,
        strategyUsed: c.strategy_used,
        reason: c.reason,
      })) ?? [],

    generatedAt: raw.generated_at,
  };
}

/**
 * STEP-3 PREVIEW (Read Only)
 */
export async function fetchStep3Preview(
  tradeDate: TradeDate
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post("/step3/preview", {
    trade_date: tradeDate,
  });

  return {
    snapshot: normalizeSnapshot(response.data.snapshot),
  };
}

/**
 * STEP-3 COMPUTE (Hybrid Manual Mode)
 *
 * Phase-1:
 *   - Sends full Step3StockContext[] from UI.
 *
 * Future Automation:
 *   - stocks will be constructed internally in backend.
 *   - frontend will stop sending manual metrics.
 */
export async function computeStep3(
  tradeDate: TradeDate,
  stocks: Step3StockContext[]
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post("/step3/compute", {
    trade_date: tradeDate,
    stocks: stocks.map((s) => ({
      symbol: s.symbol,

      avg_traded_value_20d: s.avgTradedValue20d,
      atr_pct: s.atrPct,
      abnormal_candle: s.abnormalCandle,

      stock_open_0915: s.stockOpen0915,
      stock_current_price: s.stockCurrentPrice,

      nifty_open_0915: s.niftyOpen0915,
      nifty_current_price: s.niftyCurrentPrice,

      gap_pct: s.gapPct,
      gap_hold: s.gapHold,
      price_vs_vwap: s.priceVsVwap,
      structure_valid: s.structureValid,
    })),
  });

  return {
    snapshot: normalizeSnapshot(response.data.snapshot),
  };
}

/**
 * STEP-3 FREEZE (Persist Evaluated Candidates Only)
 */
export async function freezeStep3(
  tradeDate: TradeDate,
  candidates: TradeCandidate[]
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post("/step3/freeze", {
    trade_date: tradeDate,
    candidates: candidates.map((c) => ({
      symbol: c.symbol,
      direction: c.direction,
      strategy_used: c.strategyUsed,
      reason: c.reason,
    })),
  });

  return {
    snapshot: normalizeSnapshot(response.data.snapshot),
  };
}
