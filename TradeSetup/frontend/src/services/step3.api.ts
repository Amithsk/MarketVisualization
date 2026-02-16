// frontend/src/services/step3.api.ts

import apiClient from "@/lib/apiClient";
import type { TradeDate } from "@/types/common.types";
import type { Step3ExecutionResponse } from "@/types/step3.types";

/**
 * Fetch STEP-3 preview snapshot.
 *
 * LOCKED RULES:
 * - Backend is authoritative
 * - Always call preview (never infer mode locally)
 * - Endpoint never fails due to missing automation
 */
export async function fetchStep3Preview(
  tradeDate: TradeDate
): Promise<Step3ExecutionResponse> {
  const response = await apiClient.post<Step3ExecutionResponse>(
    "/step3/preview",
    {
      trade_date: tradeDate,
    }
  );

  return response.data;
}
