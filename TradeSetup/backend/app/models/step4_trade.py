# backend/app/models/step4_trade.py

from sqlalchemy import Column, String, Date, Float, Integer, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step4Trade(Base):
    """
    STEP-4: Frozen Trade (Execution Intent)
    --------------------------------------
    Stores the final, immutable trade committed by the trader.
    This represents a money-impacting decision.
    """

    __tablename__ = "step4_trade"

    # Identity (one frozen trade per day)
    trade_date = Column(Date, primary_key=True, index=True)

    # Instrument (from STEP-3)
    symbol = Column(String(32), nullable=False)
    direction = Column(String(16), nullable=False)  # LONG / SHORT

    # Execution intent
    execution_mode = Column(String(16), nullable=False)

    # Prices
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)

    # Risk definition
    risk_percent = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Optional rationale
    rationale = Column(String(512), nullable=True)

    # Freeze metadata (irreversible)
    frozen_at = Column(DateTime, nullable=False)

    # Audit
    created_at = Column(DateTime, server_default=func.now(), nullable=False)