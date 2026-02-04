// src/services/step2.api.ts

import apiClient from "@/lib/apiClient";
import {
  Step2PreviewResponse,
  Step2FrozenResponse,
} from "@/types/step2.types";

/**
 * Fetch STEP-2 market open behavior preview for a given trade date.
 * Used before the step is frozen.
 */
export async function fetchStep2Preview(
  tradeDate: string
): Promise<Step2PreviewResponse> {
  const response = await apiClient.post<Step2PreviewResponse>(
    "/api/step2/preview",
    { tradeDate }
  );

  return response.data;
}

/**
 * Freeze STEP-2 market open behavior.
 * Once frozen, trade permission becomes authoritative for the day.
 */
export async function freezeStep2Behavior(
  tradeDate: string
): Promise<Step2FrozenResponse> {
  const response = await apiClient.post<Step2FrozenResponse>(
    "/api/step2/freeze",
    { tradeDate }
  );

  return response.data;
}