export interface StockIdentity { exchange: string; symbol: string; }
export interface SavedDate { trade_date: string; }

export interface Zone { state: string; reason?: string | null; level?: number | null; lower?: number | null; upper?: number | null; confirmation?: string | null; reaction_timestamps: string[]; }
export interface Movement { label?: string | null; points?: number | null; percent?: number | null; explanation?: string | null; }
export interface PriceMove { open?: number | null; close?: number | null; points?: number | null; percent?: number | null; }
export interface Scenario { state: string; reason?: string | null; condition?: string | null; zone?: { lower?: number; upper?: number } | null; }

export interface StockReview {
  header: { exchange: string; symbol: string; trade_date: string; candle_interval_minutes?: number | null; timezone?: string | null; };
  status: string;
  analysis_version: string;
  session: { open: number; high: number; low: number; close: number; move_points?: number | null; move_percent?: number | null; };
  movement: Movement | null;
  support: Zone;
  resistance: Zone;
  benchmark: {
    state: string; reason?: string | null; benchmark_status: string; interval_start?: string | null; interval_end?: string | null;
    stock?: PriceMove | null; benchmark?: PriceMove | null; relationship?: string | null; explanation?: string | null; reference_timestamp?: string | null;
  };
  volume_context: { state: string; reason?: string | null; comparison?: string | null; bounce_volume?: number | null; prior_five_median_volume?: number | null; bounce_timestamp?: string | null; };
  next_session_watch: { support_scenario?: Scenario | null; resistance_scenario?: Scenario | null; };
}
