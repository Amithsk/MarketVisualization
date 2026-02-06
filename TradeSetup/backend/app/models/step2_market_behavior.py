from sqlalchemy import Column, String, Date, Boolean, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step2MarketBehavior(Base):
    """
    STEP-2: Market Open Behavior (Frozen)
    -------------------------------------
    Stores observed market behavior after market open
    and whether trading is permitted for the day.

    One row per trading day.
    Becomes immutable once frozen_at is set.
    """

    __tablename__ = "step2_market_behavior"

    # =========================
    # Identity
    # =========================
    trade_date = Column(Date, primary_key=True, index=True)

    # =========================
    # Observations (categorical)
    # =========================
    # Examples (not enforced yet):
    # index_open_behavior: STRONG_UP / WEAK_UP / FLAT / WEAK_DOWN / STRONG_DOWN
    index_open_behavior = Column(String(32), nullable=False)

    # early_volatility: HIGH / NORMAL / LOW
    early_volatility = Column(String(32), nullable=False)

    # market_participation: BROAD / SELECTIVE / THIN
    market_participation = Column(String(32), nullable=False)

    # =========================
    # Decision (gatekeeper)
    # =========================
    trade_allowed = Column(Boolean, nullable=False)

    # =========================
    # Freeze metadata
    # =========================
    frozen_at = Column(DateTime, nullable=True)

    # =========================
    # Audit fields
    # =========================
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # =========================
    # Debug / logging helper
    # =========================
    def __repr__(self) -> str:
        return (
            f"<Step2MarketBehavior("
            f"trade_date={self.trade_date}, "
            f"index_open_behavior={self.index_open_behavior}, "
            f"early_volatility={self.early_volatility}, "
            f"market_participation={self.market_participation}, "
            f"trade_allowed={self.trade_allowed}, "
            f"frozen_at={self.frozen_at}"
            f")>"
        )
