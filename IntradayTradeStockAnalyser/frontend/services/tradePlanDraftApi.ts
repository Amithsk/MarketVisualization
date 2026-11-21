import type { Candle } from "../types/candle";

type DraftParams = {
  direction: "LONG" | "SHORT";
  strategy: string;
  contextTimestamp: string;
  stockCandles: Candle[];
  niftyCandles: Candle[];
  entry: string;
  stopLoss: string;
  target: string;
  invalidation: string;
  entryConfirmation: string;
};

export async function generateTradePlanDraft(params: DraftParams): Promise<string> {
  const response = await fetch("/api/v1/trades/plan-draft", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      direction: params.direction,
      strategy: params.strategy,
      context_timestamp: params.contextTimestamp,
      stock_candles: params.stockCandles,
      nifty_candles: params.niftyCandles,
      entry: params.entry,
      stop_loss: params.stopLoss,
      target: params.target,
      invalidation: params.invalidation,
      entry_confirmation: params.entryConfirmation,
    }),
  });
  const payload = await response.json();
  if (!response.ok || payload.status !== "success") {
    throw new Error(payload.detail || payload.message || "Could not generate a trade-plan draft");
  }
  return payload.draft;
}
