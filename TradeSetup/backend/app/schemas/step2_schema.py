from datetime import date, datetime
from pydantic import BaseModel, Field


# =========================
# Requests
# =========================

class Step2PreviewRequest(BaseModel):
    """
    Read-only request to preview STEP-2 context for a given trade_date.
    """
    trade_date: date


class Step2FreezeRequest(BaseModel):
    """
    Freeze request capturing observed market behavior
    after market open.
    """
    trade_date: date

    index_open_behavior: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="How the index opened (e.g. STRONG_UP, FLAT, WEAK_DOWN)"
    )

    early_volatility: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Early session volatility (e.g. HIGH, NORMAL, LOW)"
    )

    market_participation: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Market breadth / participation (e.g. BROAD, SELECTIVE, THIN)"
    )

    trade_allowed: bool = Field(
        ...,
        description="Whether trading is permitted for the day"
    )


# =========================
# Snapshot (shared)
# =========================

class Step2OpenBehaviorSnapshot(BaseModel):
    """
    Immutable STEP-2 snapshot.
    Consumed by STEP-3 to determine execution eligibility.
    """
    trade_date: date

    index_open_behavior: str
    early_volatility: str
    market_participation: str

    trade_allowed: bool

    frozen_at: datetime | None = None

    class Config:
        orm_mode = True


# =========================
# Responses
# =========================

class Step2PreviewResponse(BaseModel):
    """
    Preview response for STEP-2.
    can_freeze=false once the context is frozen.
    """
    snapshot: Step2OpenBehaviorSnapshot
    can_freeze: bool


class Step2FrozenResponse(BaseModel):
    """
    Response after STEP-2 is successfully frozen.
    """
    snapshot: Step2OpenBehaviorSnapshot
    frozen: bool = True
