// frontend/src/services/step4.api.ts

import apiClient from "@/lib/apiClient";
import type {
  TradeIntent,
  Step4FrozenTradeResponse,
} from "@/types/step4.types";

/**
 * Freeze final trade execution intent.
 * This action is irreversible.
 */
export async function freezeFinalTrade(
  tradeIntent: TradeIntent
): Promise<Step4FrozenTradeResponse> {
  const response = await apiClient.post<Step4FrozenTradeResponse>(
    "/step4/freeze",
    tradeIntent
  );

  return response.data;
}
