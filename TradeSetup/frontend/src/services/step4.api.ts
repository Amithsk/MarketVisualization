// frontend/src/services/step4.api.ts

import apiClient from "@/lib/apiClient";
import type {
  Step4PreviewRequest,
  Step4PreviewResponse,
  Step4ComputeRequest,
  Step4ComputeResponse,
  Step4FreezeRequest,
  Step4FrozenTradeResponse,
} from "@/types/step4.types";

/**
 * STEP-4 PHASE-1
 * Load structural execution blueprint from backend.
 * No risk computation happens here.
 */
export async function loadStep4Preview(
  payload: Step4PreviewRequest
): Promise<Step4PreviewResponse> {
  console.log(
    "[STEP4][API][PREVIEW][REQUEST]",
    payload
  );

  const response = await apiClient.post<Step4PreviewResponse>(
    "/step4/preview",
    payload
  );

  console.log(
    "[STEP4][API][PREVIEW][RESPONSE]",
    response.data.mode,
    response.data.candidates.length
  );

  return response.data;
}

/**
 * STEP-4 PHASE-2
 * Compute execution math (entry, stop, quantity, etc).
 */
export async function computeStep4Trade(
  payload: Step4ComputeRequest
): Promise<Step4ComputeResponse> {
  console.log(
    "[STEP4][API][COMPUTE][REQUEST]",
    payload.trade_date,
    payload.symbol
  );

  const response = await apiClient.post<Step4ComputeResponse>(
    "/step4/compute",
    payload
  );

  console.log(
    "[STEP4][API][COMPUTE][RESPONSE]",
    response.data.preview.trade_status
  );

  return response.data;
}

/**
 * STEP-4 FREEZE
 * Freeze final trade execution intent.
 * This action is irreversible.
 */
export async function freezeFinalTrade(
  payload: Step4FreezeRequest
): Promise<Step4FrozenTradeResponse> {
  console.log(
    "[STEP4][API][FREEZE][REQUEST]",
    payload.trade_date,
    payload.symbol
  );

  const response = await apiClient.post<Step4FrozenTradeResponse>(
    "/step4/freeze",
    payload
  );

  console.log(
    "[STEP4][API][FREEZE][SUCCESS]",
    response.data.trade.symbol
  );

  return response.data;
}