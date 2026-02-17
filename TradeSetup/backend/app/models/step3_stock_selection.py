# backend/app/models/step3_stock_selection.py

from sqlalchemy import Column, Date, DateTime, String, Text, Float
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3StockSelection(Base):
    """
    STEP-3B: Stock Selection (Frozen System Output)
    ------------------------------------------------
    One row per (trade_date, symbol).
    System generated.
    Immutable once created.
    """

    __tablename__ = "step3_stock_selection"

    # =========================
    # Identity (Composite PK)
    # =========================
    trade_date = Column(Date, primary_key=True, index=True)
    symbol = Column(String(32), primary_key=True)

    # =========================
    # Trade Characteristics
    # =========================
    direction = Column(String(8), nullable=False)  # LONG / SHORT

    # Enum in DB: GAP_FOLLOW / MOMENTUM
    strategy_used = Column(String(32), nullable=False)

    # Optional Relative Strength metric
    rs_value = Column(Float, nullable=True)

    # Mandatory explanation
    reason = Column(Text, nullable=False)

    # When system evaluated the stock
    evaluated_at = Column(DateTime, nullable=False)

    # =========================
    # Audit
    # =========================
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # =========================
    # Debug Helper
    # =========================
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
