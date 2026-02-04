# backend/app/models/step1_market_context.py

from sqlalchemy import Column, String, Date, Float, DateTime, Text
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step1MarketContext(Base):
    """
    STEP-1: Pre-Market Context (Frozen)
    -----------------------------------
    Stores the trader's pre-market understanding of the day,
    combined with system-derived market context.
    """

    __tablename__ = "step1_market_context"

    # Identity
    trade_date = Column(Date, primary_key=True, index=True)

    # === System-derived market data ===
    prev_close = Column(Float, nullable=False)
    prev_high = Column(Float, nullable=False)
    prev_low = Column(Float, nullable=False)

    day2_high = Column(Float, nullable=True)
    day2_low = Column(Float, nullable=True)

    preopen_price = Column(Float, nullable=True)

    # === Derived context ===
    gap_pct = Column(Float, nullable=True)
    gap_context = Column(String(32), nullable=True)
    range_context = Column(String(32), nullable=True)

    # === Trader inputs (before freeze) ===
    market_bias = Column(String(32), nullable=False, default="UNDEFINED")
    premarket_notes = Column(Text, nullable=True)

    # === Freeze metadata ===
    frozen_at = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )