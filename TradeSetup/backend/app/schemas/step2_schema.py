#backend/app/schemas/step2_schema.py
from datetime import date, datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


# =========================
# Shared enums / flags
# =========================

StepMode = Literal["AUTO", "MANUAL"]


# =========================
# Requests
# =========================

class Step2PreviewRequest(BaseModel):
    """
    Read-only request to preview STEP-2 context for a given trade_date.
    Must NEVER fail due to missing OHLCV data.
    """
    trade_date: date


class Step2CandleInput(BaseModel):
    """
    Raw 5-min OHLCV candle entered by trader (09:15–09:45).
    """
    timestamp: str = Field(..., description="HH:MM")
    open: float
    high: float
    low: float
    close: float
    volume: float


class Step2FreezeRequest(BaseModel):
    """
    Freeze request capturing ONLY raw observations.
    All decisions are derived by backend.
    """
    trade_date: date

    candles: List[Step2CandleInput] = Field(
        ...,
        description="5-minute OHLCV candles from 09:15 to 09:45"
    )

    reason: Optional[str] = Field(
        None,
        max_length=1000,
        description="One factual sentence linking observation → decision"
    )


# =========================
# Snapshot (shared)
# =========================

class Step2OpenBehaviorSnapshot(BaseModel):
    """
    Immutable STEP-2 snapshot.
    Consumed by STEP-3.
    """

    trade_date: date

    # --- Mode control ---
    mode: StepMode
    manual_input_required: bool

    # --- System baseline ---
    avg_5m_range_prev_day: Optional[float] = None

    # --- Derived observations ---
    index_open_behavior: Optional[str] = None
    early_volatility: Optional[str] = None
    market_participation: Optional[str] = None

    # --- FINAL SYSTEM DECISION ---
    trade_allowed: Optional[bool] = None

    # --- Audit ---
    frozen_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# =========================
# Responses
# =========================

class Step2PreviewResponse(BaseModel):
    """
    Preview response for STEP-2.

    - mode=MANUAL → UI must show editable OHLCV grid
    - mode=AUTO   → UI shows computed values (read-only)
    """
    snapshot: Step2OpenBehaviorSnapshot
    can_freeze: bool


class Step2FrozenResponse(BaseModel):
    """
    Response after STEP-2 is successfully frozen.
    """
    snapshot: Step2OpenBehaviorSnapshot
    frozen: bool = True
