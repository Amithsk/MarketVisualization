import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2PreviewResponse,
  Step2FrozenResponse,
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";

export async function fetchStep2Preview(
  tradeDate: TradeDate
): Promise<Step2PreviewResponse> {
  const res = await apiClient.post("/step2/preview", {
    trade_date: tradeDate,
  });

  return res.data;
}

export async function freezeStep2Behavior(params: {
  tradeDate: TradeDate;
  indexOpenBehavior: IndexOpenBehavior;
  earlyVolatility: EarlyVolatility;
  marketParticipation: MarketParticipation;
}): Promise<Step2FrozenResponse> {
  const res = await apiClient.post("/step2/freeze", {
    trade_date: params.tradeDate,
    index_open_behavior: params.indexOpenBehavior,
    early_volatility: params.earlyVolatility,
    market_participation: params.marketParticipation,
  });

  return res.data;
}
