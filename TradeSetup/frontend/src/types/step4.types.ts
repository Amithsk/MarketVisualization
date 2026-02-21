// frontend/src/types/step4.types.ts

import { TradeDate, IsoTimestamp } from "./common.types";

/**
 * STEP-4: Execution & Trade Construction
 * --------------------------------------
 * Backend is the single source of truth.
 * Frontend never derives execution values.
 */

/* =====================================================
   PREVIEW TYPES
===================================================== */

export type TradeStatus = "READY" | "BLOCKED";

export interface Step4PreviewRequest {
  trade_date: TradeDate;
  symbol: string;

  capital: number;
  risk_percent: number;
  entry_buffer: number;
  r_multiple: number;
}

export interface Step4PreviewSnapshot {
  trade_date: TradeDate;
  symbol: string;

  direction: "LONG" | "SHORT";
  strategy_used: "GAP_FOLLOW" | "MOMENTUM";

  entry_price: number;
  stop_loss: number;
  risk_per_share: number;
  quantity: number;
  target_price: number;

  trade_status: TradeStatus;
  block_reason?: string;

  constructed_at: IsoTimestamp;
}

export interface Step4PreviewResponse {
  preview: Step4PreviewSnapshot;
}


/* =====================================================
   FREEZE TYPES
===================================================== */

export interface Step4FreezeRequest {
  trade_date: TradeDate;
  symbol: string;

  capital: number;
  risk_percent: number;
  entry_buffer: number;
  r_multiple: number;

  rationale?: string;
}

export interface FrozenTrade {
  trade_date: TradeDate;

  symbol: string;
  direction: "LONG" | "SHORT";
  setup_type: "GAP_FOLLOW" | "MOMENTUM";

  entry_price: number;
  stop_loss: number;
  risk_per_share: number;
  quantity: number;
  target_price: number;

  trade_status: TradeStatus;
  block_reason?: string;

  capital: number;
  risk_percent: number;
  entry_buffer: number;
  r_multiple: number;

  rationale?: string;

  frozen_at: IsoTimestamp;
}

export interface Step4FrozenTradeResponse {
  trade: FrozenTrade;
  frozen: boolean;
}
