// frontend/src/types/step4.types.ts

import { TradeDate, IsoTimestamp } from "./common.types";

/**
 * STEP-4: Execution & Trade Construction
 * --------------------------------------
 * Backend is the single source of truth.
 * Frontend never derives execution values.
 */

/* =====================================================
   COMMON
===================================================== */

export type TradeStatus = "READY" | "BLOCKED";
export type Step4Mode = "AUTO" | "MANUAL_REQUIRED";

/* =====================================================
   PHASE-1 → PREVIEW (STRUCTURAL CONTEXT LOAD)
===================================================== */

export interface Step4PreviewRequest {
  trade_date: TradeDate;
}

export interface Step4ExecutionBlueprint {
  trade_date: TradeDate;

  symbol: string;
  direction: "LONG" | "SHORT";
  strategy_used: "GAP_FOLLOW" | "MOMENTUM";

  gap_high?: number;
  gap_low?: number;

  intraday_high?: number;
  intraday_low?: number;

  last_higher_low?: number;
  vwap_value?: number;

  structure_valid: boolean;
}

export interface Step4PreviewResponse {
  mode: Step4Mode;
  candidates: Step4ExecutionBlueprint[];
}

/* =====================================================
   PHASE-2 → COMPUTE (RISK CALCULATION)
===================================================== */

export interface Step4ComputeRequest {
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

export interface Step4ComputeResponse {
  preview: Step4PreviewSnapshot;
}

/* =====================================================
   FREEZE
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