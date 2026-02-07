// src/types/step3.types.ts

import type { TradeDate, IsoTimestamp } from "@/types/common.types";

/**
 * STEP-3: Execution Control & Candidate Selection
 * -----------------------------------------------
 * Backend is authoritative.
 * Frontend is read-only + assisted input (STEP-3.2).
 */

/**
 * Allowed trade direction.
 */
export type TradeDirection = "LONG" | "SHORT";

/**
 * High-level setup classification.
 * Purely descriptive.
 */
export type SetupType =
  | "TREND_CONTINUATION"
  | "MEAN_REVERSION"
  | "BREAKOUT"
  | "REVERSAL"
  | "UNKNOWN";

/**
 * Candidate origin mode (BACKEND AUTHORITY).
 */
export type CandidatesMode = "AUTO" | "MANUAL";

/**
 * Trade candidate (AUTO = system, MANUAL = trader).
 */
export interface TradeCandidate {
  symbol: string;
  direction: TradeDirection;
  setupType: SetupType;
  notes?: string;
}

/**
 * STEP-3 execution snapshot.
 *
 * STEP-3.1 (System):
 *  - executionEnabled
 *
 * STEP-3.2 (Backend decides):
 *  - candidatesMode
 *  - candidates list (may be empty)
 */
export interface Step3ExecutionSnapshot {
  tradeDate: TradeDate;

  /**
   * Hard gate derived from STEP-1 + STEP-2.
   */
  executionEnabled: boolean;

  /**
   * Backend-declared candidate mode.
   * AUTO   -> candidates preloaded
   * MANUAL -> frontend must allow entry
   */
  candidatesMode: CandidatesMode;

  /**
   * Candidate list.
   * Empty is a VALID state.
   */
  candidates: TradeCandidate[];

  /**
   * Generation timestamp.
   */
  generatedAt: IsoTimestamp;
}

/**
 * STEP-3 execution API response.
 */
export interface Step3ExecutionResponse {
  snapshot: Step3ExecutionSnapshot;
}
