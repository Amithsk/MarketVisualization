// src/services/step1.api.ts

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type {
  Step1PreviewResponse,
  Step1FrozenResponse,
} from "@/types/step1.types";

/**
 * Fetch STEP-1 pre-market context preview for a given trade date.
 * Used before the step is frozen.
 */
export async function fetchStep1Preview(
  tradeDate: TradeDate
): Promise<Step1PreviewResponse> {
  const response = await apiClient.post<Step1PreviewResponse>(
    "/step1/preview",
    { tradeDate }
  );

  return response.data;
}

/**
 * Freeze STEP-1 context.
 * Once frozen, it becomes immutable for the rest of the trading day.
 */
export async function freezeStep1Context(
  tradeDate: TradeDate
): Promise<Step1FrozenResponse> {
  const response = await apiClient.post<Step1FrozenResponse>(
    "/step1/freeze",
    { tradeDate }
  );

  return response.data;
}