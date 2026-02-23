//frontend/src/services/step1.api.ts
import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step1PreviewResponseDTO,
  Step1FrozenResponseDTO,
  Step1PreviewResponse,
  Step1FrozenResponse,
  Step1ContextSnapshot,
  MarketBias,
} from "@/types/step1.types";

/**
 * =========================================================
 * RAW SYSTEM INPUTS (MANUAL MODE ONLY)
 * =========================================================
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

/* =========================================================
   🔁 DTO → NORMALIZED SNAPSHOT
   ========================================================= */

function normalizeSnapshot(
  raw: Step1PreviewResponseDTO["snapshot"]
): Step1ContextSnapshot {
  return {
    tradeDate: raw!.trade_date,

    yesterdayClose: raw!.yesterday_close,
    yesterdayHigh: raw!.yesterday_high,
    yesterdayLow: raw!.yesterday_low,
    day2High: raw!.day2_high,
    day2Low: raw!.day2_low,

    last5DayRanges: raw!.last_5_day_ranges,

    preOpenPrice: raw!.pre_open_price,

    gapPct: raw!.gap_pct,
    gapClass: raw!.gap_class,

    rangeRatio: raw!.range_ratio,
    rangeSize: raw!.range_size,

    overlapType: raw!.overlap_type,
    db2State: raw!.db2_state,

    marketBias: raw!.market_bias,
    gapContext: raw!.gap_context,
    premarketNotes: raw!.premarket_notes,

    frozenAt: raw!.frozen_at,
  };
}

/* =========================================================
   STEP-1 PREVIEW
   ========================================================= */

export async function fetchStep1Preview(
  tradeDate: TradeDate
): Promise<Step1PreviewResponse> {
  console.log("[DEBUG][API][STEP-1][PREVIEW] start", {
    trade_date: tradeDate,
  });

  try {
    const response =
      await apiClient.post<Step1PreviewResponseDTO>(
        "/step1/preview",
        { trade_date: tradeDate }
      );

    const dto = response.data;

    return {
      mode: dto.mode,
      canFreeze: dto.can_freeze,
      snapshot: dto.snapshot
        ? normalizeSnapshot(dto.snapshot)
        : null,
    };
  } catch {
    console.error(
      "[DEBUG][API][STEP-1][PREVIEW] failed before response"
    );
    throw new Error("STEP-1 preview request failed");
  }
}

/* =========================================================
   STEP-1 COMPUTE (MANUAL)
   ========================================================= */

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

    return {
      derivedContext: response.data.derived_context,
      suggestedMarketContext:
        response.data.suggested_market_context,
    };
  } catch {
    console.error(
      "[DEBUG][API][STEP-1][COMPUTE] failed before response"
    );
    throw new Error("STEP-1 compute request failed");
  }
}

/* =========================================================
   STEP-1 FREEZE
   ========================================================= */

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
    const response =
      await apiClient.post<Step1FrozenResponseDTO>(
        "/step1/freeze",
        payload
      );

    return {
      frozen: true,
      snapshot: normalizeSnapshot(response.data.snapshot),
    };
  } catch {
    console.error(
      "[DEBUG][API][STEP-1][FREEZE] failed before response"
    );
    throw new Error("STEP-1 freeze request failed");
  }
}