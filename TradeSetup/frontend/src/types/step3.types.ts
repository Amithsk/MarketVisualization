// =========================================================
// File: frontend/src/types/step3.types.ts
// =========================================================

import type { TradeDate, IsoTimestamp } from "@/types/common.types";

/**
 * STEP-3: Execution Control & Stock Selection
 * -------------------------------------------
 * Backend is authoritative.
 * Frontend is display only.
 *
 * candidatesMode:
 *   - "MANUAL"  → Not frozen
 *   - "AUTO"    → Persisted (frozen) state
 *
 * canFreeze:
 *   - Backend-authoritative flag
 *   - Frontend must NOT infer freeze eligibility
 */


// =========================================================
// Layer-3 Strategy Types
// =========================================================

export type TradeDirection = "LONG" | "SHORT";

export type StrategyUsed =
  | "GAP_FOLLOW"
  | "MOMENTUM"
  | "NO_TRADE";

export type CandidatesMode = "AUTO" | "MANUAL";


// =========================================================
// Canonical Input Model (Hybrid Mode)
// MUST match backend Step3StockContext exactly
// =========================================================

export interface Step3StockContext {
  symbol: string;

  // -------------------------
  // Layer 1 — Tradability
  // -------------------------

  avgTradedValue20d: number;
  atrPct: number;
  abnormalCandle: boolean;

  // -------------------------
  // Layer 2 — RS vs NIFTY
  // -------------------------

  stockOpen0915: number;
  stockCurrentPrice: number;

  niftyOpen0915: number;
  niftyCurrentPrice: number;

  // -------------------------
  // Layer 3 — Strategy Fit
  // -------------------------

  gapPct: number;
  gapHold: boolean;
  priceVsVwap: "ABOVE" | "BELOW";
  structureValid: boolean;
}


// =========================================================
// Final Per-Stock Output (Backend Derived — Deterministic)
// MUST match backend TradeCandidate exactly
// =========================================================

export interface TradeCandidate {
  symbol: string;
  direction: TradeDirection;
  strategyUsed: StrategyUsed;

  // 🔥 ADDING LAYER-1 PREVIEW FIELDS (Optional)
  avgTradedValue20d?: number;
  atrPct?: number;
  abnormalCandle?: boolean;

  // -------------------------
  // Structural Snapshot (Frozen in STEP-3)
  // -------------------------

  rsValue?: number | null;

  gapHigh?: number | null;
  gapLow?: number | null;

  intradayHigh?: number | null;
  intradayLow?: number | null;

  lastHigherLow?: number | null;

  yesterdayClose?: number | null;
  vwapValue?: number | null;

  structureValid: boolean;

  reason: string;
}


// =========================================================
// STEP-3 Execution Snapshot
// MUST match backend Step3ExecutionSnapshot
// =========================================================

export interface Step3ExecutionSnapshot {
  tradeDate: TradeDate;

  // -------------------------
  // STEP-3A — Index Level
  // -------------------------

  marketContext: string | null;
  tradePermission: string | null;

  allowedStrategies: StrategyUsed[];
  maxTradesAllowed: number;
  executionEnabled: boolean;

  // -------------------------
  // STEP-3B — Stock Funnel
  // -------------------------

  candidatesMode: CandidatesMode;
  candidates: TradeCandidate[];

  generatedAt: IsoTimestamp;
}


// =========================================================
// API Response Types
// =========================================================

export interface Step3ExecutionResponse {
  snapshot: Step3ExecutionSnapshot;
  canFreeze: boolean; // Backend authoritative flag
}