// =========================================================
// File: frontend/src/types/step3.types.ts
// =========================================================

import type { TradeDate, IsoTimestamp } from "@/types/common.types";

/**
 * STEP-3: Execution Control & Stock Selection
 * -------------------------------------------
 * Backend is authoritative.
 * Frontend is display only.
 */


/**
 * Allowed trade direction (Layer-2 derived).
 */
export type TradeDirection = "LONG" | "SHORT";

/**
 * Strategy assigned in Layer-3.
 */
export type StrategyUsed =
  | "GAP_FOLLOW"
  | "MOMENTUM"
  | "NO_TRADE";

/**
 * Candidate origin mode (BACKEND AUTHORITY).
 */
export type CandidatesMode = "AUTO" | "MANUAL";

/**
 * Final per-stock output from STEP-3B.
 * Deterministic and backend-derived.
 */
export interface TradeCandidate {
  symbol: string;
  direction: TradeDirection;
  strategyUsed: StrategyUsed;
  reason: string;
}

/**
 * STEP-3 execution snapshot.
 *
 * MUST match backend Step3ExecutionSnapshot exactly.
 */
export interface Step3ExecutionSnapshot {
  tradeDate: TradeDate;

  // -------------------------
  // STEP-3A — Index Level
  // -------------------------

  /**
   * Market context derived from STEP-1
   * Example: TREND_DAY | RANGE_UNCERTAIN_DAY | NO_TRADE_DAY
   */
  marketContext: string;

  /**
   * Trade permission derived from STEP-2
   * Example: YES | LIMITED | NO
   */
  tradePermission: string;

  /**
   * Allowed strategies for the day.
   * Empty array is valid (NO_TRADE).
   */
  allowedStrategies: string[];

  /**
   * Maximum trades permitted today.
   */
  maxTradesAllowed: number;

  /**
   * Derived as maxTradesAllowed > 0.
   */
  executionEnabled: boolean;

  // -------------------------
  // STEP-3B — Stock Funnel
  // -------------------------

  /**
   * Backend-declared candidate mode.
   * AUTO   -> candidates preloaded
   * MANUAL -> frontend must allow entry
   */
  candidatesMode: CandidatesMode;

  /**
   * Candidate list.
   * Empty is VALID state.
   */
  candidates: TradeCandidate[];

  /**
   * Generation timestamp.
   */
  generatedAt: IsoTimestamp;
}

/**
 * STEP-3 preview API response.
 */
export interface Step3ExecutionResponse {
  snapshot: Step3ExecutionSnapshot;
}
