# backend/app/models/step4_trade_construction.py

from sqlalchemy import (
    Column,
    String,
    Date,
    Float,
    Integer,
    DateTime,
)
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step4TradeConstruction(Base):
    """
    STEP-4 Preview Layer
    ---------------------
    Stores derived execution snapshot.
    Overwritable.
    """

    __tablename__ = "step4_trade_construction"

    # Composite Primary Key
    trade_date = Column(Date, primary_key=True)
    symbol = Column(String(32), primary_key=True)

    # Strategy & Structure
    strategy_used = Column(String(32), nullable=False)
    direction = Column(String(16), nullable=False)

    structure_valid = Column(Integer, nullable=False)  # tinyint(1)

    # Derived Execution Values
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    risk_per_share = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    target_price = Column(Float, nullable=False)

    trade_status = Column(String(16), nullable=False)
    block_reason = Column(String(255), nullable=True)

    # Metadata
    constructed_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Step4TradeConstruction("
            f"date={self.trade_date}, "
            f"symbol={self.symbol}, "
            f"status={self.trade_status}, "
            f"qty={self.quantity}"
            f")>"
        )
