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
 * ARCHITECTURE NOTE (Hybrid Manual Mode)
 * ---------------------------------------
 * Phase-1:
 *   - UI supplies full Step3StockContext inputs manually.
 *   - Backend evaluates deterministically.
 *
 * Future Automation Mode:
 *   - Step3StockContext will be built from stock data pipeline.
 *   - Manual UI inputs will be removed.
 *   - Evaluation engine will remain unchanged.
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
// Final Per-Stock Output (Backend Derived)
// =========================================================

export interface TradeCandidate {
  symbol: string;
  direction: TradeDirection;
  strategyUsed: StrategyUsed;
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

  marketContext: string;
  tradePermission: string;

  allowedStrategies: string[];
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
}
