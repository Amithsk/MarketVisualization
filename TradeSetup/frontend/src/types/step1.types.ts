// src/types/step1.types.ts

import type {
  FreezeMetadata,
  TradeDate,
} from "@/types/common.types";

/**
 * STEP-1: Pre-Market Context
 * --------------------------
 * Captures the trader's market understanding BEFORE market open.
 * This data is frozen and referenced throughout the trading day.
 */

/**
 * High-level directional bias for the day.
 * This is NOT a trade signal.
 */
export type MarketBias =
  | "BULLISH"
  | "BEARISH"
  | "NEUTRAL"
  | "RANGE_BOUND"
  | "UNDEFINED";

/**
 * Opening gap behavior of the index (NIFTY).
 */
export type GapContext =
  | "GAP_UP"
  | "GAP_DOWN"
  | "FLAT"
  | "UNKNOWN";

/**
 * Core STEP-1 snapshot
 * Used in BOTH AUTO and MANUAL modes
 */
export interface Step1ContextSnapshot extends FreezeMetadata {
  tradeDate: TradeDate;

  marketBias: MarketBias;
  gapContext: GapContext;

  /**
   * Free-form notes written before market open.
   * Immutable after freeze.
   */
  preMarketNotes?: string;
}

/**
 * Response shape for STEP-1 preview API.
 * canFreeze allows UI to enable/disable Freeze action.
 */
export interface Step1PreviewResponse {
  snapshot: Step1ContextSnapshot;
  canFreeze: boolean;
}

/**
 * Response shape after STEP-1 is frozen.
 */
export interface Step1FrozenResponse {
  snapshot: Step1ContextSnapshot;
  frozen: true;
}
