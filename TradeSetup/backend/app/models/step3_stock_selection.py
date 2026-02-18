# =========================================================
# File: backend/app/models/step3_stock_selection.py
# =========================================================
"""
STEP-3B: Stock Selection (Frozen System Output)

ARCHITECTURAL PRINCIPLE
-----------------------

This table stores ONLY the FINAL deterministic evaluation result.

It does NOT store:
- Manual Layer-1 inputs
- Manual Layer-2 inputs
- Manual Layer-3 inputs

Why?

Because in future Automation Mode:
- Inputs will come from stock data pipeline.
- Engine logic will remain unchanged.
- Only evaluated result must be persisted.

This guarantees:
- Clean audit trail
- Deterministic reproducibility
- Easy migration to full automation
"""

from sqlalchemy import Column, Date, DateTime, String, Text, Float
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3StockSelection(Base):
    """
    One row per (trade_date, symbol).

    Created only during STEP-3 Freeze.
    Immutable once persisted.
    """

    __tablename__ = "step3_stock_selection"

    # =====================================================
    # Identity (Composite Primary Key)
    # =====================================================

    trade_date = Column(Date, primary_key=True, index=True)
    symbol = Column(String(32), primary_key=True)

    # =====================================================
    # Deterministic Evaluation Result
    # =====================================================

    direction = Column(String(8), nullable=False)  # LONG / SHORT

    strategy_used = Column(
        String(32),
        nullable=False
    )  # GAP_FOLLOW / MOMENTUM / NO_TRADE

    # Optional RS metric for transparency & debugging
    # In future automation mode this will be computed from pipeline
    rs_value = Column(Float, nullable=True)

    # Mandatory explanation (factual engine output)
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
            f"rs={self.rs_value}"
            f")>"
        )
