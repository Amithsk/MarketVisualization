// src/services/step1.api.ts

import apiClient from "@/lib/apiClient";
import {
  Step1PreviewResponse,
  Step1FrozenResponse,
} from "@/types/step1.types";

/**
 * Fetch STEP-1 pre-market context preview for a given trade date.
 * This is used before the step is frozen.
 */
export async function fetchStep1Preview(
  tradeDate: string
): Promise<Step1PreviewResponse> {
  const response = await apiClient.post<Step1PreviewResponse>(
    "/api/step1/preview",
    { tradeDate }
  );

  return response.data;
}

/**
 * Freeze STEP-1 context.
 * Once frozen, it becomes immutable for the rest of the trading day.
 */
export async function freezeStep1Context(
  tradeDate: string
): Promise<Step1FrozenResponse> {
  const response = await apiClient.post<Step1FrozenResponse>(
    "/api/step1/freeze",
    { tradeDate }
  );

  return response.data;
}