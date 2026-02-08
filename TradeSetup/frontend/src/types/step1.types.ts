import type { TradeDate } from "@/types/common.types";

/**
 * =========================================================
 * STEP-1: PRE-MARKET CONTEXT — FROZEN TYPES
 * =========================================================
 * - Backend is the single source of truth
 * - Frontend uses these types for rendering only
 * - No calculations happen in UI
 */

/* =========================================================
 * ENUM-LIKE CONSTANTS
 * ========================================================= */

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

/* =========================================================
 * CORE SNAPSHOT — BACKEND OWNED
 * ========================================================= */

export interface Step1ContextSnapshot {
  /* Identity */
  tradeDate: TradeDate;

  /* ==============================
   * SYSTEM MARKET DATA
   * ============================== */
  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;

  /* ==============================
   * PRE-OPEN
   * ============================== */
  preOpenPrice?: number;

  /* ==============================
   * DERIVED CONTEXT (SYSTEM)
   * ============================== */
  gapPct?: number;
  gapClass?: string;

  rangeRatio?: number;
  rangeSize?: string;

  overlapType?: string;
  db2State?: string;

  /* ==============================
   * FINAL MARKET CONTEXT
   * ============================== */
  marketBias: MarketBias;
  gapContext: GapContext;
  premarketNotes?: string;

  /* ==============================
   * FREEZE METADATA
   * ============================== */
  frozenAt?: string;
}

/* =========================================================
 * PREVIEW RESPONSE
 * ========================================================= */

export interface Step1PreviewResponse {
  mode: "AUTO" | "MANUAL";
  snapshot: Step1ContextSnapshot | null;
  canFreeze: boolean;
}

/* =========================================================
 * FREEZE RESPONSE
 * ========================================================= */

export interface Step1FrozenResponse {
  snapshot: Step1ContextSnapshot;
  frozen: true;
}

/* =========================================================
 * DEBUG HELPERS (OPTIONAL, EXPLICIT USE ONLY)
 * ========================================================= */

/**
 * Explicit debug utility.
 * Call this ONLY from hooks or components when needed.
 * Never auto-executes.
 */
export function debugStep1Snapshot(
  label: string,
  snapshot: Step1ContextSnapshot | null
) {
  console.log(`[DEBUG][STEP-1][SNAPSHOT] ${label}`, {
    snapshot,
  });
}
