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
 * Converts snake_case → camelCase
 * Preserves deterministic structural snapshot
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
      raw.candidates?.map((c: any): TradeCandidate => ({
        symbol: c.symbol,
        direction: c.direction,
        strategyUsed: c.strategy_used,

        rsValue: c.rs_value ?? null,

        gapHigh: c.gap_high ?? null,
        gapLow: c.gap_low ?? null,

        intradayHigh: c.intraday_high ?? null,
        intradayLow: c.intraday_low ?? null,

        lastHigherLow: c.last_higher_low ?? null,

        yesterdayClose: c.yesterday_close ?? null,
        vwapValue: c.vwap_value ?? null,

        structureValid: Boolean(c.structure_valid),

        reason: c.reason,
      })) ?? [],

    generatedAt: raw.generated_at,
  };
}

/**
 * STEP-3 PREVIEW
 */
export async function fetchStep3Preview(
  tradeDate: TradeDate
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post("/step3/preview", {
    trade_date: tradeDate,
  });

  return {
    snapshot: normalizeSnapshot(response.data.snapshot),
    canFreeze: response.data.can_freeze ?? false,
  };
}

/**
 * STEP-3 COMPUTE
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
    canFreeze: response.data.can_freeze ?? false,
  };
}

/**
 * STEP-3 FREEZE
 * Sends full deterministic structural snapshot
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

      rs_value: c.rsValue ?? null,

      gap_high: c.gapHigh ?? null,
      gap_low: c.gapLow ?? null,

      intraday_high: c.intradayHigh ?? null,
      intraday_low: c.intradayLow ?? null,

      last_higher_low: c.lastHigherLow ?? null,

      yesterday_close: c.yesterdayClose ?? null,
      vwap_value: c.vwapValue ?? null,

      structure_valid: c.structureValid,

      reason: c.reason,
    })),
  });

  return {
    snapshot: normalizeSnapshot(response.data.snapshot),
    canFreeze: response.data.can_freeze ?? false,
  };
}