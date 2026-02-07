# backend/app/models/step1_market_context.py

from sqlalchemy import Column, String, Date, Float, DateTime, Text
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step1MarketContext(Base):
    """
    STEP-1: Pre-Market Context (Frozen)

    Stores the FINAL trader decision for the day.
    Manual-first by design.
    One row per trading day.
    Immutable once created.
    """

    __tablename__ = "step1_market_context"

    # =========================
    # Identity
    # =========================
    trade_date = Column(
        Date,
        primary_key=True,
        index=True,
        comment="Trading date (one row per day)"
    )

    # =========================
    # Manual + derived fields
    # =========================
    preopen_price = Column(
        Float,
        nullable=True,
        comment="Manual pre-open price entered by trader"
    )

    gap_pct = Column(
        Float,
        nullable=True,
        comment="Derived gap percentage"
    )

    gap_class = Column(
        String(32),
        nullable=True,
        comment="Derived gap classification"
    )

    prior_range_size = Column(
        String(32),
        nullable=True,
        comment="Derived prior day range size"
    )

    prior_day_overlap = Column(
        String(32),
        nullable=True,
        comment="Derived prior day overlap"
    )

    prior_structure_state = Column(
        String(32),
        nullable=True,
        comment="Derived structural state"
    )

    # =========================
    # Final trader decision
    # =========================
    final_market_context = Column(
        String(32),
        nullable=False,
        comment="Final STEP-1 classification (TREND_DAY / RANGE / NO_TRADE)"
    )

    final_reason = Column(
        Text,
        nullable=False,
        comment="Mandatory factual reasoning for final decision"
    )

    # =========================
    # Audit
    # =========================
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when STEP-1 was frozen"
    )

    # =========================
    # Debug helper
    # =========================
    def __repr__(self) -> str:
        return (
            f"<Step1MarketContext("
            f"trade_date={self.trade_date}, "
            f"final_market_context={self.final_market_context}, "
            f"gap_class={self.gap_class}, "
            f"created_at={self.created_at}"
            f")>"
        )
