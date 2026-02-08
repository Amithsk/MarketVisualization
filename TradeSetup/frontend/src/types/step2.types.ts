import type { FreezeMetadata, TradeDate } from "@/types/common.types";

export type Step2Mode = "AUTO" | "MANUAL";

export type IndexOpenBehavior =
  | "STRONG_UP"
  | "WEAK_UP"
  | "FLAT"
  | "WEAK_DOWN"
  | "STRONG_DOWN"
  | "UNKNOWN";

export type EarlyVolatility =
  | "EXPANDING"
  | "CONTRACTING"
  | "NORMAL"
  | "CHAOTIC"
  | "UNKNOWN";

export type MarketParticipation =
  | "BROAD"
  | "NARROW"
  | "MIXED"
  | "THIN"
  | "UNKNOWN";

export interface Step2OpenBehaviorSnapshot extends FreezeMetadata {
  tradeDate: TradeDate;

  indexOpenBehavior: IndexOpenBehavior;
  earlyVolatility: EarlyVolatility;
  marketParticipation: MarketParticipation;

  tradeAllowed: boolean;
}

export interface Step2PreviewResponse {
  mode: Step2Mode;           // ✅ BACKEND AUTHORITY
  snapshot: Step2OpenBehaviorSnapshot;
  canFreeze: boolean;
}

export interface Step2FrozenResponse {
  snapshot: Step2OpenBehaviorSnapshot;
  frozen: true;
}
