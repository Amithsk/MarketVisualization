//backend/src/types/step1.types.ts
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
  /* ==============================
   * Identity
   * ============================== */
  tradeDate: TradeDate;

  /* ==============================
   * SYSTEM MARKET DATA (RAW)
   * Editable ONLY when backend mode = MANUAL
   * ============================== */
  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;

  /**
   * Last 5 completed trading-day ranges.
   * Order: most recent → oldest
   * Backend derived when automation exists,
   * otherwise provided manually in MANUAL mode.
   */
  last5DayRanges?: number[];

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
    tradeDate: snapshot?.tradeDate,
    modeSensitiveFields: {
      yesterdayClose: snapshot?.yesterdayClose,
      yesterdayHigh: snapshot?.yesterdayHigh,
      yesterdayLow: snapshot?.yesterdayLow,
      day2High: snapshot?.day2High,
      day2Low: snapshot?.day2Low,
      last5DayRanges: snapshot?.last5DayRanges,
    },
    derived: {
      gapPct: snapshot?.gapPct,
      gapClass: snapshot?.gapClass,
      rangeRatio: snapshot?.rangeRatio,
      rangeSize: snapshot?.rangeSize,
      overlapType: snapshot?.overlapType,
      db2State: snapshot?.db2State,
    },
    frozenAt: snapshot?.frozenAt,
  });
}

