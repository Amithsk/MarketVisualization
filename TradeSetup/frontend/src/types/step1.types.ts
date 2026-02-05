// src/types/step1.types.ts

import { FreezeMetadata, TradeDate } from "./common.types";

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
 * Core STEP-1 snapshot as returned by backend.
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
 */
export interface Step1PreviewResponse {
  snapshot: Step1ContextSnapshot;
}

/**
 * Response shape after STEP-1 is frozen.
 */
export interface Step1FrozenResponse {
  snapshot: Step1ContextSnapshot;
}