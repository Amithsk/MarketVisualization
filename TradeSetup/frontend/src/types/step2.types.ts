// frontend/src/types/step2.types.ts

import type { TradeDate, IsoTimestamp } from "@/types/common.types";

/**
 * Backend authoritative mode
 */
export type Step2Mode = "AUTO" | "MANUAL";

/* =====================================================
   ENUMS (Must match backend exactly)
===================================================== */

export type VolatilityState =
  | "EXPANDING"
  | "CONTRACTING"
  | "NORMAL"
  | "CHAOTIC";

export type VWAPState =
  | "ABOVE_VWAP"
  | "BELOW_VWAP"
  | "MIXED";

export type RangeHoldStatus =
  | "HELD"
  | "BROKEN_UP"
  | "BROKEN_DOWN";

/**
 * Raw 5-min candle input
 * Used for COMPUTE and FREEZE
 */
export interface Step2CandleInput {
  timestamp: string; // "09:15"
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Snapshot MUST match backend schema EXACTLY.
 * No camelCase conversion.
 */
export interface Step2OpenBehaviorSnapshot {
  trade_date: TradeDate;

  /* --- Mode control --- */
  mode: Step2Mode;
  manual_input_required: boolean;

  /* --- System baseline --- */
  avg_5m_range_prev_day: number | null;

  /* =====================================================
     FULL ANALYTICAL BREAKDOWN (Option B)
  ===================================================== */

  /* Initial Range */
  ir_high: number | null;
  ir_low: number | null;
  ir_range: number | null;
  ir_ratio: number | null;

  /* Volatility */
  volatility_state: VolatilityState | null;

  /* VWAP */
  vwap_cross_count: number | null;
  vwap_state: VWAPState | null;

  /* Range Integrity */
  range_hold_status: RangeHoldStatus | null;

  /* =====================================================
     Derived Behavioral Classification
  ===================================================== */

  index_open_behavior: string | null;
  early_volatility: string | null;
  market_participation: string | null;

  /* --- Final decision --- */
  trade_allowed: boolean | null;

  /* --- Audit --- */
  frozen_at: IsoTimestamp | null;
}

/**
 * Preview response
 */
export interface Step2PreviewResponse {
  snapshot: Step2OpenBehaviorSnapshot;
  can_freeze: boolean;
}

/**
 * Compute response (NEW)
 */
export interface Step2ComputeResponse {
  snapshot: Step2OpenBehaviorSnapshot;
  can_freeze: boolean;
}

/**
 * Freeze response
 */
export interface Step2FrozenResponse {
  snapshot: Step2OpenBehaviorSnapshot;
  frozen: true;
}
