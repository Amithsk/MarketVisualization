# backend/app/schemas/step1_schema.py

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# -------------------------
# Requests
# -------------------------

class Step1PreviewRequest(BaseModel):
    trade_date: date


class Step1FreezeRequest(BaseModel):
    trade_date: date
    market_bias: str = Field(..., description="Trader's directional bias")
    premarket_notes: Optional[str] = None


# -------------------------
# Snapshot (shared)
# -------------------------

class Step1ContextSnapshot(BaseModel):
    trade_date: date

    # System-derived market data
    prev_close: float
    prev_high: float
    prev_low: float

    day2_high: Optional[float] = None
    day2_low: Optional[float] = None
    preopen_price: Optional[float] = None

    # Derived context
    gap_pct: Optional[float] = None
    gap_context: Optional[str] = None
    range_context: Optional[str] = None

    # Trader inputs
    market_bias: str
    premarket_notes: Optional[str] = None

    # Freeze metadata
    frozen_at: Optional[datetime] = None


# -------------------------
# Responses
# -------------------------

class Step1PreviewResponse(BaseModel):
    snapshot: Step1ContextSnapshot
    can_freeze: bool


class Step1FrozenResponse(BaseModel):
    snapshot: Step1ContextSnapshot
    frozen: bool = True