//frontend/src/services/step1.api.ts
import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step1PreviewResponse,
  Step1FrozenResponse,
  MarketBias,
} from "@/types/step1.types";

/**
 * Raw system inputs used ONLY in MANUAL mode
 */
export type Step1ComputePayload = {
  yesterdayClose: number;
  yesterdayHigh: number;
  yesterdayLow: number;
  day2High: number;
  day2Low: number;
  last5DayRanges: number[];
  preOpenPrice: number;
};

export type Step1ComputeResponse = {
  derivedContext: Record<string, number | string>;
  suggestedMarketContext:
    | "TREND_DAY"
    | "RANGE_UNCERTAIN_DAY"
    | "NO_TRADE_DAY";
};

/**
 * Fetch STEP-1 pre-market context preview.
 */
export async function fetchStep1Preview(
  tradeDate: TradeDate
): Promise<Step1PreviewResponse> {
  console.log("[DEBUG][API][STEP-1][PREVIEW] start", {
    trade_date: tradeDate,
  });

  try {
    const response = await apiClient.post<Step1PreviewResponse>(
      "/step1/preview",
      { trade_date: tradeDate }
    );

    console.log("[DEBUG][API][STEP-1][PREVIEW] success", {
      mode: response.data.mode,
    });

    return response.data;
  } catch {
    console.error(
      "[DEBUG][API][STEP-1][PREVIEW] failed before response"
    );
    throw new Error("STEP-1 preview request failed");
  }
}

/**
 * Compute STEP-1 derived context (MANUAL mode only).
 */
export async function computeStep1Context(
  payload: Step1ComputePayload
): Promise<Step1ComputeResponse> {
  const requestBody = {
    yesterday_close: payload.yesterdayClose,
    yesterday_high: payload.yesterdayHigh,
    yesterday_low: payload.yesterdayLow,
    day2_high: payload.day2High,
    day2_low: payload.day2Low,
    last_5_day_ranges: payload.last5DayRanges,
    preopen_price: payload.preOpenPrice,
  };

  console.log("[DEBUG][API][STEP-1][COMPUTE] start", requestBody);

  try {
    const response = await apiClient.post(
      "/step1/compute",
      requestBody
    );

    const mapped: Step1ComputeResponse = {
      derivedContext: response.data.derived_context,
      suggestedMarketContext:
        response.data.suggested_market_context,
    };

    console.log(
      "[DEBUG][API][STEP-1][COMPUTE] mapped response",
      mapped
    );

    return mapped;
  } catch {
    console.error(
      "[DEBUG][API][STEP-1][COMPUTE] failed before response"
    );
    throw new Error("STEP-1 compute request failed");
  }
}

/**
 * Freeze STEP-1 context (AUTHORITATIVE SNAPSHOT)
 */
export async function freezeStep1Context(params: {
  tradeDate: TradeDate;
  marketBias: MarketBias;
  gapContext: string;
  preMarketNotes?: string;
  preOpenPrice: number;
  derivedContext: Record<string, number | string>;
}): Promise<Step1FrozenResponse> {
  const payload = {
    trade_date: params.tradeDate,
    market_bias: params.marketBias,
    gap_context: params.gapContext,
    premarket_notes: params.preMarketNotes ?? null,

    preopen_price: params.preOpenPrice,
    derived_context: params.derivedContext,
  };

  console.log("[DEBUG][API][STEP-1][FREEZE] start", payload);

  try {
    const response = await apiClient.post<Step1FrozenResponse>(
      "/step1/freeze",
      payload
    );

    console.log("[DEBUG][API][STEP-1][FREEZE] success", {
      frozenAt: response.data.snapshot.frozenAt,
    });

    return response.data;
  } catch {
    console.error(
      "[DEBUG][API][STEP-1][FREEZE] failed before response"
    );
    throw new Error("STEP-1 freeze request failed");
  }
}
