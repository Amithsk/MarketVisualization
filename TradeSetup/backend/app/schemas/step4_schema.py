from datetime import date, datetime
from pydantic import BaseModel, Field


# =========================
# Requests
# =========================

class Step4FreezeRequest(BaseModel):
    """
    Freeze a STEP-4 trade.

    This is a money-impacting, irreversible action.
    All validations here are defensive.
    """

    trade_date: date

    # -------------------------
    # Instrument (must come from STEP-3)
    # -------------------------
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Instrument symbol (must exist in STEP-3)"
    )

    direction: str = Field(
        ...,
        min_length=4,
        max_length=16,
        description="Trade direction (LONG / SHORT)"
    )

    setup_type: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Setup type from STEP-3 (traceability)"
    )

    # -------------------------
    # Execution intent
    # -------------------------
    execution_mode: str = Field(
        ...,
        min_length=3,
        max_length=16,
        description="Execution mode (MARKET, LIMIT, VWAP, etc.)"
    )

    # -------------------------
    # Prices
    # -------------------------
    entry_price: float = Field(
        ...,
        gt=0,
        description="Intended entry price"
    )

    stop_loss: float = Field(
        ...,
        gt=0,
        description="Protective stop-loss price"
    )

    # -------------------------
    # Risk definition
    # -------------------------
    risk_percent: float = Field(
        ...,
        gt=0,
        le=5.0,
        description="Risk per trade as % of capital (hard-capped)"
    )

    quantity: int = Field(
        ...,
        gt=0,
        description="Trade quantity (must be > 0)"
    )

    # -------------------------
    # Optional rationale
    # -------------------------
    rationale: str | None = Field(
        None,
        max_length=512,
        description="Optional trader rationale"
    )


# =========================
# Snapshot
# =========================

class FrozenTradeSnapshot(BaseModel):
    """
    Immutable snapshot of a frozen STEP-4 trade.
    """

    trade_date: date

    symbol: str
    direction: str
    setup_type: str
    execution_mode: str

    entry_price: float
    stop_loss: float

    risk_percent: float
    quantity: int

    rationale: str | None = None

    frozen_at: datetime

    class Config:
        orm_mode = True


# =========================
# Response
# =========================

class Step4FrozenTradeResponse(BaseModel):
    """
    Response after a STEP-4 trade is frozen.
    """
    trade: FrozenTradeSnapshot
    frozen: bool = True
