# backend/app/models/step1_market_context.py

import logging
from sqlalchemy import Column, String, Date, Float, DateTime, Text
from sqlalchemy.sql import func
from backend.app.db.base import Base

logger = logging.getLogger(__name__)


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
        comment="Trading date (one row per day)",
    )

    # =========================
    # Manual + derived fields
    # =========================
    preopen_price = Column(
        Float,
        nullable=True,
        comment="Manual pre-open price entered by trader",
    )

    gap_pct = Column(
        Float,
        nullable=True,
        comment="Derived gap percentage",
    )

    gap_class = Column(
        String(32),
        nullable=True,
        comment="Derived gap classification",
    )

    prior_range_size = Column(
        String(32),
        nullable=True,
        comment="Derived prior day range size",
    )

    prior_day_overlap = Column(
        String(32),
        nullable=True,
        comment="Derived prior day overlap",
    )

    prior_structure_state = Column(
        String(32),
        nullable=True,
        comment="Derived structural state",
    )

    # =========================
    # Final trader decision
    # =========================
    final_market_context = Column(
        String(32),
        nullable=False,
        comment="Final STEP-1 classification (TREND_DAY / RANGE / NO_TRADE)",
    )

    final_reason = Column(
        Text,
        nullable=False,
        comment="Mandatory factual reasoning for final decision",
    )

    # =========================
    # Audit
    # =========================
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when STEP-1 was frozen",
    )

    # =========================
    # Debug helpers
    # =========================
    def __repr__(self) -> str:
        """
        Compact representation for logs and debugging.
        """
        return (
            f"<Step1MarketContext("
            f"trade_date={self.trade_date}, "
            f"final_market_context={self.final_market_context}, "
            f"gap_class={self.gap_class}, "
            f"prior_structure_state={self.prior_structure_state}, "
            f"created_at={self.created_at}"
            f")>"
        )

    def log_state(self, prefix: str = "[STEP-1][MODEL]"):
        """
        Explicit debug logger for inspecting persisted state.
        Safe to call from services.
        """
        logger.debug(
            "%s trade_date=%s preopen_price=%s gap_pct=%s gap_class=%s "
            "prior_range_size=%s prior_day_overlap=%s prior_structure_state=%s "
            "final_market_context=%s created_at=%s",
            prefix,
            self.trade_date,
            self.preopen_price,
            self.gap_pct,
            self.gap_class,
            self.prior_range_size,
            self.prior_day_overlap,
            self.prior_structure_state,
            self.final_market_context,
            self.created_at,
        )
