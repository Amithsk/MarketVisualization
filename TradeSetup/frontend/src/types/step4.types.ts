// frontend/src/types/step4.types.ts

import { TradeDate, IsoTimestamp, FreezeMetadata } from "./common.types";

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
 * Trade intent BEFORE freeze.
 * This is what the UI constructs and sends to backend.
 */
export interface TradeIntent {
  tradeDate: TradeDate;

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
   */
  quantity: number;

  /**
   * Optional rationale written at commit time.
   */
  rationale?: string;
}

/**
 * Core frozen trade object as returned by backend.
 * IMMUTABLE after creation.
 */
export interface FrozenTrade extends FreezeMetadata {
  tradeDate: TradeDate;

  symbol: string;
  direction: FinalTradeDirection;

  executionMode: ExecutionMode;

  entryPrice: number;
  stopLoss: number;

  riskPercent: number;
  quantity: number;

  rationale?: string;

  /**
   * Audit timestamp
   */
  frozenAt: IsoTimestamp;
}

/**
 * Response shape after STEP-4 freeze.
 */
export interface Step4FrozenTradeResponse {
  trade: FrozenTrade;
}
