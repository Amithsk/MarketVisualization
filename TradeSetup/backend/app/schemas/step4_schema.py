# backend/app/schemas/step4_schema.py

from datetime import date, datetime
from pydantic import BaseModel, Field


# =====================================================
# STEP-4 PREVIEW
# =====================================================

class Step4PreviewRequest(BaseModel):
    """
    Generate / overwrite STEP-4 construction snapshot.
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
    Derived preview snapshot (construction layer).
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
    block_reason: str | None = None

    constructed_at: datetime


class Step4PreviewResponse(BaseModel):
    """
    Response after STEP-4 preview generation.
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

    rationale: str | None = Field(
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
    block_reason: str | None = None

    capital: float
    risk_percent: float
    entry_buffer: float
    r_multiple: float

    rationale: str | None = None

    frozen_at: datetime

    class Config:
        orm_mode = True


class Step4FrozenTradeResponse(BaseModel):
    """
    Response after a STEP-4 trade is frozen.
    """
    trade: FrozenTradeSnapshot
    frozen: bool = True
