// src/types/step2.types.ts

/**
 * STEP-2: Market Open Behavior
 * ----------------------------
 * Captures how the market actually behaved after open.
 * This step gates whether trading is allowed for the day.
 */

/**
 * How the index opened relative to expectations / prior close.
 */
export type IndexOpenBehavior =
  | "STRONG_UP"
  | "WEAK_UP"
  | "FLAT"
  | "WEAK_DOWN"
  | "STRONG_DOWN"
  | "UNKNOWN";

/**
 * Early-session volatility assessment.
 */
export type EarlyVolatility =
  | "EXPANDING"
  | "CONTRACTING"
  | "NORMAL"
  | "CHAOTIC"
  | "UNKNOWN";

/**
 * Broad market participation quality.
 */
export type MarketParticipation =
  | "BROAD"
  | "NARROW"
  | "MIXED"
  | "THIN"
  | "UNKNOWN";

/**
 * Core STEP-2 snapshot as shown in the UI.
 */
export interface Step2OpenBehaviorSnapshot {
  tradeDate: string;

  indexOpenBehavior: IndexOpenBehavior;
  earlyVolatility: EarlyVolatility;
  marketParticipation: MarketParticipation;

  /**
   * Whether trading is permitted after evaluating STEP-2.
   * This is a hard gate for STEP-3 and STEP-4.
   */
  tradeAllowed: boolean;

  /**
   * When STEP-2 was frozen.
   * Null = not frozen yet.
   */
  frozenAt: string | null;
}

/**
 * Response shape for STEP-2 preview API.
 */
export interface Step2PreviewResponse {
  snapshot: Step2OpenBehaviorSnapshot;
  canFreeze: boolean;
}

/**
 * Response shape after STEP-2 is frozen.
 */
export interface Step2FrozenResponse {
  snapshot: Step2OpenBehaviorSnapshot;
  frozen: true;
}