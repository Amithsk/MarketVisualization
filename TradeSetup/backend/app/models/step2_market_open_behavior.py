#backend/app/models/step2_market_open_behavior.py
from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step2MarketOpenBehavior(Base):
    """
    STEP-2: Market Open Analytical Snapshot (Frozen)
    ------------------------------------------------
    Stores derived open metrics (IR, VWAP, volatility, etc.)
    One row per trading day.
    """

    __tablename__ = "step2_market_open_behavior"

    trade_date = Column(Date, primary_key=True, index=True)

    ir_high = Column(Float, nullable=False)
    ir_low = Column(Float, nullable=False)
    ir_range = Column(Float, nullable=False)
    ir_ratio = Column(Float, nullable=False)

    volatility_state = Column(String(16), nullable=False)
    vwap_cross_count = Column(Integer, nullable=False)
    vwap_state = Column(String(16), nullable=False)
    range_hold_status = Column(String(16), nullable=False)

    trade_permission = Column(String(16), nullable=False)
    reason = Column(Text, nullable=False)

    decision_locked_at = Column(DateTime, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Step2MarketOpenBehavior(trade_date={self.trade_date})>"
