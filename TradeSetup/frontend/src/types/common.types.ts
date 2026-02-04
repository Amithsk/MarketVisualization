// src/types/common.types.ts

/**
 * Common, shared types used across multiple steps.
 */

/**
 * Standard API error shape (normalized by apiClient).
 */
export interface ApiError {
  status?: number;
  message: string;
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