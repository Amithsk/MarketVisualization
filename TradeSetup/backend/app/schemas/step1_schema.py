from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# =========================
# Requests
# =========================

class Step1PreviewRequest(BaseModel):
    """
    Read-only request.
    Returns a computed snapshot for the given trade_date.
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
        description="Trader's directional bias (e.g. BULLISH, BEARISH, NEUTRAL)"
    )

    premarket_notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional discretionary notes before market open"
    )


# =========================
# Snapshot (shared)
# =========================

class Step1ContextSnapshot(BaseModel):
    """
    Unified snapshot returned by preview and freeze endpoints.
    """
    trade_date: date

    # --- System-derived market data ---
    prev_close: float
    prev_high: float
    prev_low: float

    day2_high: Optional[float] = None
    day2_low: Optional[float] = None
    preopen_price: Optional[float] = None

    # --- Derived context ---
    gap_pct: Optional[float] = None
    gap_context: Optional[str] = None
    range_context: Optional[str] = None

    # --- Trader inputs ---
    market_bias: str
    premarket_notes: Optional[str] = None

    # --- Freeze metadata ---
    frozen_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# =========================
# Responses
# =========================

class Step1PreviewResponse(BaseModel):
    """
    Preview response.
    can_freeze=false when market is closed, holiday, or already frozen.
    """
    snapshot: Step1ContextSnapshot
    can_freeze: bool


class Step1FrozenResponse(BaseModel):
    """
    Immutable response after successful freeze.
    """
    snapshot: Step1ContextSnapshot
    frozen: bool = True
