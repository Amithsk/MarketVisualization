# backend/app/models/step2_market_behavior.py

from sqlalchemy import Column, String, Date, Boolean, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step2MarketBehavior(Base):
    """
    STEP-2: Market Open Behavior (Frozen)
    -------------------------------------
    Stores observed market behavior after open and
    whether trading is permitted for the day.
    """

    __tablename__ = "step2_market_behavior"

    # Identity
    trade_date = Column(Date, primary_key=True, index=True)

    # === Observations ===
    index_open_behavior = Column(String(32), nullable=False)
    early_volatility = Column(String(32), nullable=False)
    market_participation = Column(String(32), nullable=False)

    # === Decision ===
    trade_allowed = Column(Boolean, nullable=False)

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