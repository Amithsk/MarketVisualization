# backend/app/schemas/step4_schema.py

from datetime import date, datetime
from pydantic import BaseModel, Field


# -------------------------
# Requests
# -------------------------

class Step4FreezeRequest(BaseModel):
    trade_date: date

    # Instrument (must come from STEP-3)
    symbol: str = Field(..., description="Instrument symbol")
    direction: str = Field(..., description="Trade direction (LONG / SHORT)")

    # Execution intent
    execution_mode: str = Field(
        ..., description="Execution mode (MARKET, LIMIT, etc.)"
    )

    # Prices
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)

    # Risk definition
    risk_percent: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

    # Optional rationale
    rationale: str | None = None


# -------------------------
# Snapshot
# -------------------------

class FrozenTradeSnapshot(BaseModel):
    trade_date: date

    symbol: str
    direction: str
    execution_mode: str

    entry_price: float
    stop_loss: float

    risk_percent: float
    quantity: int

    rationale: str | None = None

    frozen_at: datetime


# -------------------------
# Response
# -------------------------

class Step4FrozenTradeResponse(BaseModel):
    trade: FrozenTradeSnapshot
    frozen: bool = True