# backend/app/schemas/step2_schema.py

from datetime import date, datetime
from pydantic import BaseModel, Field


# -------------------------
# Requests
# -------------------------

class Step2PreviewRequest(BaseModel):
    trade_date: date


class Step2FreezeRequest(BaseModel):
    trade_date: date

    index_open_behavior: str = Field(..., description="How the index opened")
    early_volatility: str = Field(..., description="Early session volatility")
    market_participation: str = Field(..., description="Breadth / participation")

    trade_allowed: bool = Field(
        ..., description="Whether trading is permitted for the day"
    )


# -------------------------
# Snapshot (shared)
# -------------------------

class Step2OpenBehaviorSnapshot(BaseModel):
    trade_date: date

    index_open_behavior: str
    early_volatility: str
    market_participation: str

    trade_allowed: bool

    frozen_at: datetime | None = None


# -------------------------
# Responses
# -------------------------

class Step2PreviewResponse(BaseModel):
    snapshot: Step2OpenBehaviorSnapshot
    can_freeze: bool


class Step2FrozenResponse(BaseModel):
    snapshot: Step2OpenBehaviorSnapshot
    frozen: bool = True