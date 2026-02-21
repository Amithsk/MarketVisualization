// frontend/src/services/step4.api.ts

import apiClient from "@/lib/apiClient";
import type {
  Step4PreviewRequest,
  Step4PreviewResponse,
  Step4FreezeRequest,
  Step4FrozenTradeResponse,
} from "@/types/step4.types";

/**
 * Generate / overwrite STEP-4 preview.
 * Computes derived execution values in backend.
 */
export async function generateStep4Preview(
  payload: Step4PreviewRequest
): Promise<Step4PreviewResponse> {
  const response = await apiClient.post<Step4PreviewResponse>(
    "/step4/preview",
    payload
  );

  return response.data;
}

/**
 * Freeze final trade execution intent.
 * This action is irreversible.
 */
export async function freezeFinalTrade(
  payload: Step4FreezeRequest
): Promise<Step4FrozenTradeResponse> {
  const response = await apiClient.post<Step4FrozenTradeResponse>(
    "/step4/freeze",
    payload
  );

  return response.data;
}
