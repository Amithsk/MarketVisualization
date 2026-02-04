// src/types/step3.types.ts

/**
 * STEP-3: Execution Control & Stock Selection
 * -------------------------------------------
 * Produces a deterministic, read-only list of trade candidates
 * based on STEP-1 and STEP-2 outcomes.
 */

/**
 * Allowed trade direction for a candidate.
 */
export type TradeDirection = "LONG" | "SHORT";

/**
 * High-level classification of the setup.
 * (Used only for labeling / review, not execution logic)
 */
export type SetupType =
  | "TREND_CONTINUATION"
  | "MEAN_REVERSION"
  | "BREAKOUT"
  | "REVERSAL"
  | "UNKNOWN";

/**
 * A single eligible trade candidate.
 */
export interface TradeCandidate {
  symbol: string;

  /**
   * Direction allowed for the day.
   * LONG or SHORT — never both.
   */
  direction: TradeDirection;

  /**
   * Why this symbol is eligible today.
   * Purely descriptive.
   */
  setupType: SetupType;

  /**
   * Optional system notes (read-only).
   */
  notes?: string;
}

/**
 * Core STEP-3 snapshot as shown in the UI.
 */
export interface Step3ExecutionSnapshot {
  tradeDate: string;

  /**
   * Whether STEP-3 is active.
   * Depends on STEP-1 and STEP-2 being frozen
   * AND tradeAllowed === true.
   */
  executionEnabled: boolean;

  /**
   * Deterministic list of eligible trade candidates.
   * Empty list is a valid outcome.
   */
  candidates: TradeCandidate[];

  /**
   * When STEP-3 was generated.
   * This step is not "frozen" — it is regenerated.
   */
  generatedAt: string;
}

/**
 * Response shape for STEP-3 execution preview.
 */
export interface Step3ExecutionResponse {
  snapshot: Step3ExecutionSnapshot;
}