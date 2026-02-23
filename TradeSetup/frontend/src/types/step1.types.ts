//frontend/src/types/step1.types.ts
import type { TradeDate } from "@/types/common.types";

/**
 * =========================================================
 * STEP-1: PRE-MARKET CONTEXT — FROZEN TYPES
 * =========================================================
 * Backend = source of truth
 * UI = render only
 * Hooks = normalization boundary
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
 * 🔒 BACKEND DTO (SNAKE_CASE — EXACT API CONTRACT)
 * ========================================================= */

export interface Step1SnapshotDTO {
  trade_date: TradeDate;

  yesterday_close?: number;
  yesterday_high?: number;
  yesterday_low?: number;
  day2_high?: number;
  day2_low?: number;

  last_5_day_ranges?: number[];

  pre_open_price?: number;

  gap_pct?: number;
  gap_class?: string;

  range_ratio?: number;
  range_size?: string;

  overlap_type?: string;
  db2_state?: string;

  market_bias: MarketBias;
  gap_context: GapContext;
  premarket_notes?: string;

  frozen_at?: string;
}

export interface Step1PreviewResponseDTO {
  mode: "AUTO" | "MANUAL";
  snapshot: Step1SnapshotDTO | null;
  can_freeze: boolean;
}

export interface Step1FrozenResponseDTO {
  snapshot: Step1SnapshotDTO;
  frozen: true;
}

/* =========================================================
 * 🧠 FRONTEND NORMALIZED SNAPSHOT (camelCase)
 * ========================================================= */

export interface Step1ContextSnapshot {
  tradeDate: TradeDate;

  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;

  last5DayRanges?: number[];

  preOpenPrice?: number;

  gapPct?: number;
  gapClass?: string;

  rangeRatio?: number;
  rangeSize?: string;

  overlapType?: string;
  db2State?: string;

  marketBias: MarketBias;
  gapContext: GapContext;
  premarketNotes?: string;

  frozenAt?: string;
}

export interface Step1PreviewResponse {
  mode: "AUTO" | "MANUAL";
  snapshot: Step1ContextSnapshot | null;
  canFreeze: boolean;
}

export interface Step1FrozenResponse {
  snapshot: Step1ContextSnapshot;
  frozen: true;
}

/* =========================================================
 * DEBUG HELPER
 * ========================================================= */

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