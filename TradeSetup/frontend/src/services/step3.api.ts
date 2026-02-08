// src/services/step3.api.ts

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type { Step3ExecutionResponse } from "@/types/step3.types";

/**
 * Fetch STEP-3 execution control snapshot.
 * This endpoint is read-only and deterministic.
 */
export async function fetchStep3Execution(
  tradeDate: TradeDate
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post<Step3ExecutionResponse>(
    "/step3/execute",
    { trade_date: tradeDate, }
  );

  return response.data;
}