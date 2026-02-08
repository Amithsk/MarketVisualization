# backend/app/schemas/step1_schema.py

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# =========================
# Requests
# =========================

class Step1PreviewRequest(BaseModel):
    trade_date: date


class Step1FreezeRequest(BaseModel):
    trade_date: date

    # Trader inputs (MANUAL mode only)
    market_bias: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Trader view of market bias"
    )

    gap_context: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Gap up / gap down / flat"
    )

    premarket_notes: Optional[str] = Field(
        None,
        max_length=1000
    )


# =========================
# Snapshot
# =========================

class Step1ContextSnapshot(BaseModel):
    trade_date: date

    # SYSTEM DATA (read-only)
    yesterday_close: Optional[float] = None
    yesterday_high: Optional[float] = None
    yesterday_low: Optional[float] = None

    # DERIVED / TRADER
    market_bias: Optional[str] = None
    gap_context: Optional[str] = None
    premarket_notes: Optional[str] = None

    frozen_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =========================
# Responses
# =========================

class Step1PreviewResponse(BaseModel):
    """
    Backend is EXPLICIT about mode.
    Frontend must NOT infer.
    """
    mode: Literal["AUTO", "MANUAL"]
    snapshot: Step1ContextSnapshot
    can_freeze: bool


class Step1FrozenResponse(BaseModel):
    snapshot: Step1ContextSnapshot
    frozen: bool = True
