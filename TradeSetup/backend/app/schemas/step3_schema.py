# =========================================================
# File: backend/app/schemas/step3_schema.py
# =========================================================
"""
STEP-3 Schema — Hybrid Structural Snapshot Mode

ARCHITECTURAL GUARANTEE
-----------------------

- Snapshot is immutable view model.
- candidates_mode represents PERSISTED state only.
- can_freeze represents backend-determined freeze eligibility.
- Structural levels are frozen during STEP-3 freeze.
- STEP-4 must never recompute structure.

This schema supports:
- Manual input (today)
- Automated pipeline (future)
- Deterministic replay
"""

from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# =========================================================
# Canonical Input Model (Engine Input)
# =========================================================

class Step3StockContext(BaseModel):

    symbol: str = Field(..., min_length=1, max_length=32)

    # Layer 1 — Tradability
    avg_traded_value_20d: float
    atr_pct: float
    abnormal_candle: bool

    # Layer 2 — RS vs NIFTY
    stock_open_0915: float
    stock_current_price: float
    nifty_open_0915: float
    nifty_current_price: float

    # Layer 3 — Strategy Fit
    gap_pct: float
    gap_hold: bool
    price_vs_vwap: Literal["ABOVE", "BELOW"]
    structure_valid: bool


# =========================================================
# Trade Candidate (Final Structural Snapshot)
# =========================================================

class TradeCandidate(BaseModel):

    symbol: str = Field(..., min_length=1, max_length=32)

    direction: Literal["LONG", "SHORT"]

    strategy_used: Literal["GAP_FOLLOW", "MOMENTUM", "NO_TRADE"]

    # ============================
    # Structural Snapshot Fields
    # ============================

    rs_value: Optional[float] = None

    # GAP Strategy
    gap_high: Optional[float] = None
    gap_low: Optional[float] = None

    # Intraday Structure
    intraday_high: Optional[float] = None
    intraday_low: Optional[float] = None

    # Momentum Structure
    last_higher_low: Optional[float] = None

    # Reference Values
    yesterday_close: Optional[float] = None
    vwap_value: Optional[float] = None

    structure_valid: bool = True

    # Mandatory engine explanation
    reason: str = Field(
        ...,
        min_length=3,
        max_length=1000,
    )


# =========================================================
# STEP-3 Snapshot (Immutable View Model)
# =========================================================

class Step3ExecutionSnapshot(BaseModel):

    trade_date: date

    # STEP-3A
    market_context: Optional[str]
    trade_permission: Optional[str]

    allowed_strategies: List[Literal["GAP_FOLLOW", "MOMENTUM"]] = Field(default_factory=list)
    max_trades_allowed: int = Field(ge=0)
    execution_enabled: bool

    # STEP-3B
    candidates_mode: Literal["AUTO", "MANUAL"]
    candidates: List[TradeCandidate] = Field(default_factory=list)

    # Metadata
    generated_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# Preview Response
# =========================================================

class Step3ExecutionResponse(BaseModel):
    """
    Used by preview endpoint.
    """
    snapshot: Step3ExecutionSnapshot
    can_freeze: bool = False


# =========================================================
# STEP-3 COMPUTE
# =========================================================

class Step3ComputeRequest(BaseModel):
    trade_date: date
    stocks: List[Step3StockContext] = Field(..., min_items=1)


class Step3ComputeResponse(BaseModel):
    """
    Compute evaluates only (NO persistence).
    Structural fields are included for preview.
    """
    snapshot: Step3ExecutionSnapshot
    can_freeze: bool


# =========================================================
# STEP-3 FREEZE
# =========================================================

class Step3FreezeRequest(BaseModel):
    trade_date: date
    candidates: List[TradeCandidate] = Field(..., min_items=1)


class Step3FreezeResponse(BaseModel):
    """
    Freeze persists full deterministic structural snapshot.
    """
    snapshot: Step3ExecutionSnapshot
    can_freeze: bool = False