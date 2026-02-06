from sqlalchemy import Column, Date, String, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3StockSelection(Base):
    """
    STEP-3: Stock Selection
    -----------------------
    Stores system-generated, read-only trade candidates
    for a given trading day.

    One row per (trade_date, symbol).
    Immutable once created.
    """

    __tablename__ = "step3_stock_selection"

    # =========================
    # Identity (composite key)
    # =========================
    trade_date = Column(Date, primary_key=True, index=True)
    symbol = Column(String(32), primary_key=True)

    # =========================
    # Trade characteristics
    # =========================
    # Execution direction (LONG / SHORT)
    direction = Column(String(16), nullable=False)

    # High-level setup classification
    setup_type = Column(String(32), nullable=False)

    # Optional system notes
    notes = Column(String(256), nullable=True)

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
            f"<Step3StockSelection("
            f"trade_date={self.trade_date}, "
            f"symbol={self.symbol}, "
            f"direction={self.direction}, "
            f"setup_type={self.setup_type}"
            f")>"
        )
