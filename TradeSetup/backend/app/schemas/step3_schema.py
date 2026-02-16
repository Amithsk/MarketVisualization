# backend/app/schemas/step3_schema.py

from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# =========================
# Trade Candidate (Per Stock Output)
# =========================

class TradeCandidate(BaseModel):
    """
    STEP-3B Final Per-Stock Output (Deterministic, Read-Only)

    This represents the result AFTER:
    - Layer 1 (Tradability)
    - Layer 2 (RS Alignment)
    - Layer 3 (Strategy Fit)

    It is NOT an execution order.
    """

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Trading symbol (e.g. RELIANCE)"
    )

    direction: Literal["LONG", "SHORT"] = Field(
        ...,
        description="Direction derived from RS alignment"
    )

    strategy_used: Literal["GAP_FOLLOW", "MOMENTUM", "NO_TRADE"] = Field(
        ...,
        description="Final assigned strategy after Layer-3 evaluation"
    )

    reason: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="One factual sentence explaining qualification or rejection"
    )


# =========================
# STEP-3 Snapshot
# =========================

class Step3ExecutionSnapshot(BaseModel):
    """
    Immutable STEP-3 Snapshot

    STEP-3A:
        - How much trading is allowed today (system-derived)

    STEP-3B:
        - Whether candidates are AUTO-loaded or MANUAL entry required
        - Final per-stock strategy classification
    """

    trade_date: date

    # =========================
    # STEP-3A — Strategy & Risk Control (Index Level)
    # =========================

    allowed_strategies: List[str] = Field(
        default_factory=list,
        description="Allowed strategies for the day (e.g. GAP_FOLLOW, MOMENTUM)"
    )

    max_trades_allowed: int = Field(
        ...,
        ge=0,
        description="Maximum number of trades permitted today"
    )

    execution_enabled: bool = Field(
        ...,
        description="True if max_trades_allowed > 0"
    )

    # =========================
    # STEP-3B — Candidate Mode
    # =========================

    candidates_mode: Literal["AUTO", "MANUAL"] = Field(
        ...,
        description="AUTO = system-loaded candidates, MANUAL = trader must add"
    )

    candidates: List[TradeCandidate] = Field(
        default_factory=list,
        description="System-generated or manually-entered evaluated candidates"
    )

    # =========================
    # Metadata
    # =========================

    generated_at: datetime

    class Config:
        orm_mode = True


# =========================
# Response Wrapper
# =========================

class Step3ExecutionResponse(BaseModel):
    """
    STEP-3 Preview / Execution Response
    """
    snapshot: Step3ExecutionSnapshot
