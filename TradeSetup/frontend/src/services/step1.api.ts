//frontend/src/services/step1.api.ts
import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step1PreviewResponse,
  Step1FrozenResponse,
  MarketBias,
} from "@/types/step1.types";

type SystemMarketData = {
  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;
};

/**
 * Fetch STEP-1 pre-market context preview.
 * Backend decides AUTO vs MANUAL.
 */
export async function fetchStep1Preview(
  tradeDate: TradeDate
): Promise<Step1PreviewResponse> {
  console.log("[DEBUG][API][STEP-1][PREVIEW] request", {
    trade_date: tradeDate,
  });

  try {
    const response = await apiClient.post<Step1PreviewResponse>(
      "/step1/preview",
      {
        trade_date: tradeDate,
      }
    );

    console.log(
      "[DEBUG][API][STEP-1][PREVIEW] response",
      response.data
    );

    return response.data;
  } catch (error) {
    console.error(
      "[DEBUG][API][STEP-1][PREVIEW] error",
      error
    );
    throw error;
  }
}

/**
 * Freeze STEP-1 context.
 * Trader inputs only.
 * Backend re-derives and locks snapshot.
 */
export async function freezeStep1Context(params: {
  tradeDate: TradeDate;
  marketBias: MarketBias;
  gapContext?: string;
  preOpenPrice?: number;
  preMarketNotes?: string;
  systemMarketData?: SystemMarketData;
}): Promise<Step1FrozenResponse> {
  const payload = {
    trade_date: params.tradeDate,
    market_bias: params.marketBias,
    gap_context: params.gapContext ?? null,
    pre_open_price: params.preOpenPrice ?? null,

    // 🔒 System Market Data (manual)
    yesterday_close:
      params.systemMarketData?.yesterdayClose ?? null,
    yesterday_high:
      params.systemMarketData?.yesterdayHigh ?? null,
    yesterday_low:
      params.systemMarketData?.yesterdayLow ?? null,
    day2_high:
      params.systemMarketData?.day2High ?? null,
    day2_low:
      params.systemMarketData?.day2Low ?? null,

    premarket_notes: params.preMarketNotes ?? null,
  };

  console.log(
    "[DEBUG][API][STEP-1][FREEZE] request",
    payload
  );

  try {
    const response = await apiClient.post<Step1FrozenResponse>(
      "/step1/freeze",
      payload
    );

    console.log(
      "[DEBUG][API][STEP-1][FREEZE] response",
      response.data
    );

    return response.data;
  } catch (error) {
    console.error(
      "[DEBUG][API][STEP-1][FREEZE] error",
      error
    );
    throw error;
  }
}
