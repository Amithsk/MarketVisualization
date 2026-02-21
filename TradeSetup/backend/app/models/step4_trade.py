# backend/app/models/step4_trade.py

from sqlalchemy import (
    Column,
    String,
    Date,
    Float,
    Integer,
    DateTime,
    BigInteger,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step4Trade(Base):
    """
    STEP-4: Frozen Trade (Execution Intent)
    --------------------------------------
    Immutable committed trade snapshot.
    """

    __tablename__ = "step4_trade"

    __table_args__ = (
        UniqueConstraint(
            "trade_date",
            "symbol",
            name="ux_step4_trade_date_symbol",
        ),
    )

    # =========================
    # Identity
    # =========================
    trade_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    trade_date = Column(Date, nullable=False, index=True)

    # =========================
    # Link to STEP-3 (source)
    # =========================
    symbol = Column(String(32), nullable=False)
    direction = Column(String(16), nullable=False)
    setup_type = Column(String(32), nullable=False)

    # =========================
    # Prices (copied from construction)
    # =========================
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)

    # =========================
    # Risk definition
    # =========================
    risk_percent = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    # =========================
    # Optional rationale
    # =========================
    rationale = Column(String(512), nullable=True)

    # =========================
    # Freeze metadata
    # =========================
    frozen_at = Column(DateTime, nullable=False)

    # =========================
    # Audit fields
    # =========================
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # =========================
    # Debug helper
    # =========================
    def __repr__(self) -> str:
        return (
            f"<Step4Trade("
            f"id={self.trade_id}, "
            f"date={self.trade_date}, "
            f"symbol={self.symbol}, "
            f"dir={self.direction}, "
            f"qty={self.quantity}, "
            f"entry={self.entry_price}, "
            f"stop={self.stop_loss}"
            f")>"
        )
