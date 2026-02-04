// src/services/step4.api.ts

import apiClient from "@/lib/apiClient";
import { FrozenTrade, Step4FrozenTradeResponse } from "@/types/step4.types";

/**
 * Freeze final trade execution intent.
 * This action is irreversible.
 */
export async function freezeFinalTrade(
  trade: FrozenTrade
): Promise<Step4FrozenTradeResponse> {
  const response = await apiClient.post<Step4FrozenTradeResponse>(
    "/api/step4/freeze",
    trade
  );

  return response.data;
}