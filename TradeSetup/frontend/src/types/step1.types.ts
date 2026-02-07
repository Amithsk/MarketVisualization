// src/types/step1.types.ts

import type { TradeDate } from "@/types/common.types";

/**
 * STEP-1: Pre-Market Context
 */

export const MARKET_BIAS_VALUES = [
  "BULLISH",
  "BEARISH",
  "NEUTRAL",
  "RANGE_BOUND",
  "UNDEFINED",
] as const;

export type MarketBias = typeof MARKET_BIAS_VALUES[number];

export const GAP_CONTEXT_VALUES = [
  "GAP_UP",
  "GAP_DOWN",
  "FLAT",
  "UNKNOWN",
] as const;

export type GapContext = typeof GAP_CONTEXT_VALUES[number];

export interface Step1ContextSnapshot {
  tradeDate: TradeDate;
  marketBias: MarketBias;
  gapContext: GapContext;
  premarketNotes?: string;
  frozenAt?: string;
}

export interface Step1PreviewResponse {
  snapshot: Step1ContextSnapshot;
  canFreeze: boolean;
}

export interface Step1FrozenResponse {
  snapshot: Step1ContextSnapshot;
  frozen: true;
}
