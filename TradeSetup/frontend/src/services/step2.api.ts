// src/services/step2.api.ts

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step2PreviewResponse,
  Step2FrozenResponse,
} from "@/types/step2.types";

/**
 * Fetch STEP-2 market open behavior preview for a given trade date.
 * Used before the step is frozen.
 */
export async function fetchStep2Preview(
  tradeDate: TradeDate
): Promise<Step2PreviewResponse> {
  const response = await apiClient.post<Step2PreviewResponse>(
    "/step2/preview",
    { tradeDate }
  );

  return response.data;
}

/**
 * Freeze STEP-2 market open behavior.
 * Once frozen, trade permission becomes authoritative for the day.
 */
export async function freezeStep2Behavior(
  tradeDate: TradeDate
): Promise<Step2FrozenResponse> {
  const response = await apiClient.post<Step2FrozenResponse>(
    "/step2/freeze",
    { tradeDate }
  );

  return response.data;
}