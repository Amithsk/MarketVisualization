from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# =========================
# Trade candidate (read-only)
# =========================

class TradeCandidate(BaseModel):
    """
    System-suggested or manually-entered trade candidate.
    Informational only — NOT an execution order.
    """
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Trading symbol (e.g. RELIANCE)"
    )

    direction: str = Field(
        ...,
        min_length=2,
        max_length=16,
        description="Trade direction (e.g. LONG / SHORT)"
    )

    setup_type: str = Field(
        ...,
        min_length=2,
        max_length=32,
        description="Setup classification (e.g. OPEN_RANGE_BREAKOUT)"
    )

    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional system or discretionary notes"
    )


# =========================
# Execution snapshot
# =========================

class Step3ExecutionSnapshot(BaseModel):
    """
    Immutable STEP-3 execution verdict.

    STEP-3.1: execution control (system)
    STEP-3.2: candidate source (system vs manual)
    """
    trade_date: date

    # ---- STEP-3.1 (System) ----
    execution_enabled: bool
    generated_at: datetime

    # ---- STEP-3.2 (Candidate selection mode) ----
    candidates_mode: Literal["AUTO", "MANUAL"] = Field(
        ...,
        description="AUTO = system-loaded candidates, MANUAL = trader must add"
    )

    candidates: List[TradeCandidate] = Field(
        default_factory=list,
        description="System-generated or manually-added candidates"
    )

    class Config:
        orm_mode = True


# =========================
# Response
# =========================

class Step3ExecutionResponse(BaseModel):
    """
    STEP-3 execution response.
    """
    snapshot: Step3ExecutionSnapshot
