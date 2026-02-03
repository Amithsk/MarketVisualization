// src/types/step4.types.ts

/**
 * STEP-4: Execution & Trade Construction
 * --------------------------------------
 * Captures the final, frozen trade intent for the day.
 * This object represents a money-impacting decision.
 */

/**
 * Final trade direction.
 */
export type FinalTradeDirection = "LONG" | "SHORT";

/**
 * How the trade is intended to be executed.
 */
export type ExecutionMode =
  | "MARKET"
  | "LIMIT"
  | "STOP_MARKET"
  | "STOP_LIMIT";

/**
 * Core frozen trade object.
 */
export interface FrozenTrade {
  tradeDate: string;

  /**
   * Instrument details (from STEP-3).
   */
  symbol: string;
  direction: FinalTradeDirection;

  /**
   * Execution intent.
   */
  executionMode: ExecutionMode;

  /**
   * Prices explicitly committed by the trader.
   */
  entryPrice: number;
  stopLoss: number;

  /**
   * Risk definition.
   * Percentage of total capital risked.
   */
  riskPercent: number;

  /**
   * Quantity is explicitly committed.
   * No auto-sizing at execution time.
   */
  quantity: number;

  /**
   * Optional rationale written at commit time.
   */
  rationale?: string;

  /**
   * When the trade was frozen.
   * This timestamp makes the trade immutable.
   */
  frozenAt: string;
}

/**
 * Response shape after STEP-4 freeze.
 */
export interface Step4FrozenTradeResponse {
  trade: FrozenTrade;
  frozen: true;
}