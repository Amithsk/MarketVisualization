import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step1PreviewResponse,
  Step1FrozenResponse,
  MarketBias,
} from "@/types/step1.types";

/**
 * Fetch STEP-1 pre-market context preview.
 * Backend decides AUTO vs MANUAL.
 */
export async function fetchStep1Preview(
  tradeDate: TradeDate
): Promise<Step1PreviewResponse> {
  const response = await apiClient.post<Step1PreviewResponse>(
    "/step1/preview",
    {
      trade_date: tradeDate, // backend expects snake_case
    }
  );

  return response.data;
}

/**
 * Freeze STEP-1 context.
 * Trader inputs only.
 */
export async function freezeStep1Context(params: {
  tradeDate: TradeDate;
  marketBias: MarketBias;
  preMarketNotes?: string;
}): Promise<Step1FrozenResponse> {
  const response = await apiClient.post<Step1FrozenResponse>(
    "/step1/freeze",
    {
      trade_date: params.tradeDate,
      market_bias: params.marketBias,
      premarket_notes: params.preMarketNotes ?? null,
    }
  );

  return response.data;
}
