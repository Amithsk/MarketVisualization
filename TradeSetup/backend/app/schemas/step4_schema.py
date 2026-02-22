# backend/app/schemas/step4_schema.py

from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List, Optional


# =====================================================
# STEP-4 PREVIEW (PHASE-1: CONTEXT LOAD)
# =====================================================

class Step4PreviewRequest(BaseModel):
    """
    STEP-4 Preview (Phase-1)
    Loads structural execution blueprint from STEP-3.
    No risk computation happens here.
    """

    trade_date: date


class Step4ExecutionBlueprint(BaseModel):
    """
    Structural snapshot from STEP-3 (Read-Only).
    Used to populate STEP-4 UI.
    """

    trade_date: date
    symbol: str
    direction: str
    strategy_used: str

    gap_high: Optional[float] = None
    gap_low: Optional[float] = None

    intraday_high: Optional[float] = None
    intraday_low: Optional[float] = None

    last_higher_low: Optional[float] = None
    vwap_value: Optional[float] = None

    structure_valid: bool


class Step4PreviewResponse(BaseModel):
    """
    Response after STEP-4 Preview (Phase-1).
    Returns structural blueprint only.
    """

    mode: str  # AUTO / MANUAL_REQUIRED
    candidates: List[Step4ExecutionBlueprint]


# =====================================================
# STEP-4 COMPUTE (PHASE-2)
# =====================================================

class Step4ComputeRequest(BaseModel):
    """
    STEP-4 Compute (Phase-2)
    Performs deterministic execution math.
    """

    trade_date: date

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Instrument symbol (must exist in STEP-3 snapshot)"
    )

    capital: float = Field(
        ...,
        gt=0,
        description="Total trading capital"
    )

    risk_percent: float = Field(
        ...,
        gt=0,
        le=5.0,
        description="Risk per trade as % of capital"
    )

    entry_buffer: float = Field(
        ...,
        ge=0,
        description="Buffer added to breakout level"
    )

    r_multiple: float = Field(
        ...,
        gt=0,
        description="Target R multiple"
    )


class Step4PreviewSnapshot(BaseModel):
    """
    Derived execution snapshot (construction layer).
    Returned after compute.
    """

    trade_date: date
    symbol: str
    direction: str
    strategy_used: str

    entry_price: float
    stop_loss: float
    risk_per_share: float
    quantity: int
    target_price: float

    trade_status: str
    block_reason: Optional[str] = None

    constructed_at: datetime


class Step4ComputeResponse(BaseModel):
    """
    Response after STEP-4 compute.
    """
    preview: Step4PreviewSnapshot


# =====================================================
# STEP-4 FREEZE
# =====================================================

class Step4FreezeRequest(BaseModel):
    """
    Freeze a STEP-4 trade.
    """

    trade_date: date

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Instrument symbol (must exist in STEP-3 snapshot)"
    )

    capital: float = Field(
        ...,
        gt=0,
        description="Total trading capital"
    )

    risk_percent: float = Field(
        ...,
        gt=0,
        le=5.0,
        description="Risk per trade as % of capital"
    )

    entry_buffer: float = Field(
        ...,
        ge=0,
        description="Buffer added to breakout level"
    )

    r_multiple: float = Field(
        ...,
        gt=0,
        description="Target R multiple"
    )

    rationale: Optional[str] = Field(
        None,
        max_length=512,
        description="Optional trader rationale"
    )


class FrozenTradeSnapshot(BaseModel):
    """
    Immutable snapshot of a frozen STEP-4 trade.
    """

    trade_date: date

    symbol: str
    direction: str
    setup_type: str

    entry_price: float
    stop_loss: float
    risk_per_share: float
    quantity: int
    target_price: float

    trade_status: str
    block_reason: Optional[str] = None

    capital: float
    risk_percent: float
    entry_buffer: float
    r_multiple: float

    rationale: Optional[str] = None

    frozen_at: datetime

    class Config:
        orm_mode = True


class Step4FrozenTradeResponse(BaseModel):
    """
    Response after a STEP-4 trade is frozen.
    """
    trade: FrozenTradeSnapshot
    frozen: bool = True