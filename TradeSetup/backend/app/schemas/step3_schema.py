# backend/app/schemas/step3_schema.py

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel


# -------------------------
# Trade candidate
# -------------------------

class TradeCandidate(BaseModel):
    symbol: str
    direction: str
    setup_type: str
    notes: Optional[str] = None


# -------------------------
# Execution snapshot
# -------------------------

class Step3ExecutionSnapshot(BaseModel):
    trade_date: date

    execution_enabled: bool
    generated_at: datetime

    candidates: List[TradeCandidate]


# -------------------------
# Response
# -------------------------

class Step3ExecutionResponse(BaseModel):
    snapshot: Step3ExecutionSnapshot