// src/services/step3.api.ts

import apiClient from "@/lib/apiClient";
import { Step3ExecutionResponse } from "@/types/step3.types";

/**
 * Fetch STEP-3 execution control snapshot.
 * This endpoint is read-only and deterministic.
 */
export async function fetchStep3Execution(
  tradeDate: string
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post<Step3ExecutionResponse>(
    "/api/step3/execute",
    { tradeDate }
  );

  return response.data;
}