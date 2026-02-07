// src/services/step2.api.ts

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2PreviewResponse,
  Step2FrozenResponse,
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";

/**
 * STEP-2 Preview
 *
 * Backend ALWAYS responds successfully.
 * UNKNOWN values indicate manual input required.
 */
export async function fetchStep2Preview(
  tradeDate: TradeDate
): Promise<Step2PreviewResponse> {
  const response = await apiClient.post<Step2PreviewResponse>(
    "/step2/preview",
    {
      trade_date: tradeDate, // snake_case backend contract
    }
  );

  return response.data;
}

/**
 * STEP-2 Freeze
 *
 * Trader submits observed behavior.
 * Backend derives tradeAllowed authoritatively.
 */
export async function freezeStep2Behavior(params: {
  tradeDate: TradeDate;
  indexOpenBehavior: IndexOpenBehavior;
  earlyVolatility: EarlyVolatility;
  marketParticipation: MarketParticipation;
  tradeAllowed: boolean;
}): Promise<Step2FrozenResponse> {
  const response = await apiClient.post<Step2FrozenResponse>(
    "/step2/freeze",
    {
      trade_date: params.tradeDate,
      index_open_behavior: params.indexOpenBehavior,
      early_volatility: params.earlyVolatility,
      market_participation: params.marketParticipation,
      trade_allowed: params.tradeAllowed,
    }
  );

  return response.data;
}
