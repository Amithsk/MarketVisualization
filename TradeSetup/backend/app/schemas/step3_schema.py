# =========================================================
# File: backend/app/schemas/step3_schema.py
# =========================================================
"""
STEP-3 Schema — Hybrid Manual Mode (Automation-Ready)

IMPORTANT ARCHITECTURAL NOTE
----------------------------

STEP-3 is being developed in PHASE-1 (Hybrid Manual Mode).

In this phase:
- Trader manually provides Layer-1 / Layer-2 / Layer-3 inputs.
- Backend runs deterministic evaluation engine.
- Freeze persists ONLY final evaluated output.

FUTURE AUTOMATION MIGRATION PLAN
---------------------------------
When stock data pipeline is implemented:

1. Step3StockContext will be constructed internally from pipeline.
2. Manual input fields will be removed from UI.
3. The evaluation engine will remain unchanged.
4. Compute endpoint will stop accepting manual metrics.
5. No change required to TradeCandidate or Snapshot model.

This ensures:
- Zero rewrite of engine logic
- Clean switch to automation
- Deterministic and ML-traceable architecture
"""

from datetime import date, datetime
from typing import List, Literal
from pydantic import BaseModel, Field


# =========================================================
# Canonical Input Model (Engine Input)
# =========================================================

class Step3StockContext(BaseModel):
    """
    Canonical per-stock evaluation input.

    In Hybrid Mode:
        Values come from manual UI entry.

    In Future Automation Mode:
        Values will be constructed from stock data pipeline.

    The deterministic evaluation engine MUST ONLY depend on this model.
    """

    symbol: str = Field(..., min_length=1, max_length=32)

    # -------------------------
    # Layer 1 — Tradability
    # -------------------------

    avg_traded_value_20d: float = Field(
        ...,
        description="20-day average traded value in Crores"
    )

    atr_pct: float = Field(
        ...,
        description="ATR percentage of stock"
    )

    abnormal_candle: bool = Field(
        ...,
        description="True if abnormal rejection candle detected"
    )

    # -------------------------
    # Layer 2 — RS vs NIFTY
    # -------------------------

    stock_open_0915: float
    stock_current_price: float

    nifty_open_0915: float
    nifty_current_price: float

    # -------------------------
    # Layer 3 — Strategy Fit Inputs
    # -------------------------

    gap_pct: float

    gap_hold: bool = Field(
        ...,
        description="True if gap hold condition satisfied"
    )

    price_vs_vwap: Literal["ABOVE", "BELOW"]

    structure_valid: bool = Field(
        ...,
        description="True if HH/HL or LH/LL structure intact"
    )


# =========================================================
# Trade Candidate (Final Evaluated Output)
# =========================================================

class TradeCandidate(BaseModel):
    """
    STEP-3B Final Per-Stock Output (Deterministic)

    This represents the FINAL evaluation result AFTER:
    - Layer 1 (Tradability)
    - Layer 2 (RS Alignment)
    - Layer 3 (Strategy Fit)

    IMPORTANT:
    Only these values are persisted on freeze.
    Manual metrics are NOT persisted.
    """

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=32,
    )

    direction: Literal["LONG", "SHORT"]

    strategy_used: Literal["GAP_FOLLOW", "MOMENTUM", "NO_TRADE"]

    reason: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="One factual sentence explaining qualification or rejection"
    )


# =========================================================
# STEP-3 Snapshot (Immutable View Model)
# =========================================================

class Step3ExecutionSnapshot(BaseModel):
    """
    Immutable STEP-3 Snapshot

    This model remains unchanged when migrating to automation.
    """

    trade_date: date

    # -------------------------
    # STEP-3A — Index Level
    # -------------------------

    market_context: str
    trade_permission: str

    allowed_strategies: List[str] = Field(default_factory=list)
    max_trades_allowed: int = Field(ge=0)
    execution_enabled: bool

    # -------------------------
    # STEP-3B — Candidate Mode
    # -------------------------

    candidates_mode: Literal["AUTO", "MANUAL"]
    candidates: List[TradeCandidate] = Field(default_factory=list)

    # -------------------------
    # Metadata
    # -------------------------

    generated_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# Preview Response (Read-Only)
# =========================================================

class Step3ExecutionResponse(BaseModel):
    snapshot: Step3ExecutionSnapshot


# =========================================================
# STEP-3 COMPUTE (Evaluate Only — No Persist)
# =========================================================

class Step3ComputeRequest(BaseModel):
    """
    Hybrid Manual Mode Input

    In Phase-1:
        stocks are manually supplied from UI.

    In Future Automation:
        This request model may no longer be exposed publicly.
        Instead, backend will construct Step3StockContext internally.
    """

    trade_date: date

    stocks: List[Step3StockContext] = Field(
        ...,
        min_items=1,
        description="List of per-stock evaluation contexts"
    )


class Step3ComputeResponse(BaseModel):
    snapshot: Step3ExecutionSnapshot


# =========================================================
# STEP-3 FREEZE (Persist Final Evaluated Candidates)
# =========================================================

class Step3FreezeRequest(BaseModel):
    """
    Freeze persists ONLY final evaluated results.

    Manual metrics are NOT stored.
    This preserves deterministic audit trail.
    """

    trade_date: date

    candidates: List[TradeCandidate] = Field(
        ...,
        min_items=1,
    )


class Step3FreezeResponse(BaseModel):
    snapshot: Step3ExecutionSnapshot
