// src/types/common.types.ts

/**
 * Common, shared types used across multiple steps.
 */

/**
 * Normalized API error shape (from apiClient).
 * status is always present (defaults to 500).
 */
export interface ApiError {
  status: number;
  message: string;
  raw?: any;
}

/**
 * Generic async state wrapper used by all STEP hooks.
 */
export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

/**
 * Freeze lifecycle state for any step.
 */
export type FreezeStatus = "NOT_FROZEN" | "FROZEN";

/**
 * Standard timestamp string (ISO 8601).
 * Example: 2026-02-01T09:15:00Z
 */
export type IsoTimestamp = string;

/**
 * Common metadata included with frozen snapshots.
 */
export interface FreezeMetadata {
  freezeStatus: FreezeStatus;
  frozenAt: IsoTimestamp | null;
}

/**
 * Common success response used by freeze endpoints.
 */
export interface ApiSuccess {
  status: "OK" | "FROZEN" | "TRADE_FROZEN";
  message?: string;
}

/**
 * Utility type for date-scoped API calls.
 */
export type TradeDate = string; // YYYY-MM-DD