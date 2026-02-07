# backend/app/schemas/step1_schema.py

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# =========================
# Requests
# =========================

class Step1PreviewRequest(BaseModel):
    """
    Read-only request.
    Returns AUTO or MANUAL mode for the given trade_date.
    """
    trade_date: date


class Step1FreezeRequest(BaseModel):
    """
    Trader intent submission.
    Only trader-controlled fields are accepted here.
    """
    trade_date: date

    market_bias: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Final market context (TREND_DAY, RANGE_UNCERTAIN_DAY, NO_TRADE_DAY)"
    )

    premarket_notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Mandatory factual reasoning for STEP-1 decision"
    )


# =========================
# Snapshot (persisted STEP-1 only)
# =========================

class Step1ContextSnapshot(BaseModel):
    """
    Snapshot of frozen STEP-1 context.
    This reflects ONLY what is stored in DB.
    """
    trade_date: date

    market_bias: str
    gap_context: Optional[str] = None
    premarket_notes: Optional[str] = None

    frozen_at: datetime

    class Config:
        orm_mode = True


# =========================
# Responses
# =========================

class Step1PreviewResponse(BaseModel):
    """
    Preview response.

    mode:
    - AUTO   → STEP-1 already exists (read-only)
    - MANUAL → Trader must input STEP-1 data

    snapshot:
    - Present only when mode = AUTO
    """
    mode: Literal["AUTO", "MANUAL"]
    snapshot: Optional[Step1ContextSnapshot]
    can_freeze: bool


class Step1FrozenResponse(BaseModel):
    """
    Immutable response after successful freeze.
    """
    snapshot: Step1ContextSnapshot
    frozen: bool = True
