from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# =========================
# Trade candidate (read-only)
# =========================

class TradeCandidate(BaseModel):
    """
    System-suggested trade candidate.
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

    If execution_enabled = false,
    candidates will typically be an empty list.
    """
    trade_date: date

    execution_enabled: bool
    generated_at: datetime

    candidates: List[TradeCandidate] = []

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
