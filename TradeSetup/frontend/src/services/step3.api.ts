// =========================================================
// File: frontend/src/services/step3.api.ts
// =========================================================

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step3ExecutionResponse,
  Step3ExecutionSnapshot,
} from "@/types/step3.types";

/**
 * Fetch STEP-3 preview snapshot.
 *
 * LOCKED RULES:
 * - Backend is authoritative
 * - Always call preview (never infer mode locally)
 * - Endpoint never fails due to missing automation
 */
export async function fetchStep3Preview(
  tradeDate: TradeDate
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post("/step3/preview", {
    trade_date: tradeDate,
  });

  const raw = response.data.snapshot;

  // 🔥 Normalize backend (snake_case) → frontend (camelCase)
  const normalized: Step3ExecutionSnapshot = {
    tradeDate: raw.trade_date,

    // STEP-3A
    marketContext: raw.market_context,
    tradePermission: raw.trade_permission,
    allowedStrategies: raw.allowed_strategies ?? [],
    maxTradesAllowed: raw.max_trades_allowed,
    executionEnabled: raw.execution_enabled,

    // STEP-3B
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

  return {
    snapshot: normalized,
  };
}
