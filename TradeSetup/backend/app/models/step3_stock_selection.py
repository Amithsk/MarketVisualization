# =========================================================
# File: backend/app/models/step3_stock_selection.py
# =========================================================
"""
STEP-3B: Stock Selection (Frozen Structural Snapshot)

ARCHITECTURAL PRINCIPLE
-----------------------

This table stores the FINAL deterministic structural snapshot
produced during STEP-3 freeze.

It persists:

1) Direction decision
2) Strategy used
3) Relative strength value
4) Structural price levels required for STEP-4 execution
5) Immutable audit timestamp

This guarantees:
- Deterministic replay
- Execution reproducibility
- Automation readiness
- STEP-4 purity (no structural recalculation)
"""

from sqlalchemy import Column, Date, DateTime, String, Text, Float, Integer
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3StockSelection(Base):
    """
    One row per (trade_date, symbol).

    Created only during STEP-3 Freeze.
    Immutable once persisted.

    This row acts as the structural execution blueprint for STEP-4.
    """

    __tablename__ = "step3_stock_selection"

    # =====================================================
    # Identity (Composite Primary Key)
    # =====================================================

    trade_date = Column(Date, primary_key=True, index=True)
    symbol = Column(String(32), primary_key=True)

    # =====================================================
    # Deterministic Decision Output
    # =====================================================

    direction = Column(String(8), nullable=False)  # LONG / SHORT

    strategy_used = Column(
        String(32),
        nullable=False
    )  # GAP_FOLLOW / MOMENTUM / NO_TRADE

    # Relative Strength snapshot at evaluation time
    rs_value = Column(Float, nullable=True)

    # =====================================================
    # Structural Snapshot (NEW — Required for STEP-4)
    # =====================================================

    # GAP strategy levels
    gap_high = Column(Float, nullable=True)
    gap_low = Column(Float, nullable=True)

    # Intraday structure
    intraday_high = Column(Float, nullable=True)
    intraday_low = Column(Float, nullable=True)

    # Momentum structure level
    last_higher_low = Column(Float, nullable=True)

    # Reference values
    yesterday_close = Column(Float, nullable=True)
    vwap_value = Column(Float, nullable=True)

    # Structural validation flag (frozen truth)
    structure_valid = Column(Integer, nullable=False, default=1)

    # =====================================================
    # Engine Explanation
    # =====================================================

    # Mandatory factual explanation (Layer-1/2/3 outcome)
    reason = Column(Text, nullable=False)

    # Timestamp when engine evaluated this stock
    evaluated_at = Column(DateTime, nullable=False)

    # =====================================================
    # Audit Metadata
    # =====================================================

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # =====================================================
    # Debug Helper
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<Step3StockSelection("
            f"trade_date={self.trade_date}, "
            f"symbol={self.symbol}, "
            f"direction={self.direction}, "
            f"strategy={self.strategy_used}, "
            f"rs={self.rs_value}, "
            f"gap_high={self.gap_high}, "
            f"gap_low={self.gap_low}, "
            f"intraday_high={self.intraday_high}, "
            f"last_higher_low={self.last_higher_low}"
            f")>"
        )