# backend/app/models/step3_execution_control.py

from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3ExecutionControl(Base):
    """
    STEP-3 Execution Control (Final Frozen Snapshot)
    ------------------------------------------------
    One row per trading day.
    Derived from STEP-1 + STEP-2.
    """

    __tablename__ = "step3_execution_control"

    # =========================
    # Identity
    # =========================
    trade_date = Column(Date, primary_key=True, index=True)

    # =========================
    # STEP-3A Decision Context
    # =========================
    market_context = Column(String(32), nullable=False)
    trade_permission = Column(String(16), nullable=False)

    # =========================
    # Derived Controls
    # =========================
    allowed_strategies = Column(String(64), nullable=False)
    max_trades_allowed = Column(Integer, nullable=False)

    execution_allowed = Column(Integer, nullable=False)

    # =========================
    # Decision Timestamp
    # =========================
    decided_at = Column(DateTime, nullable=False)

    # =========================
    # Audit
    # =========================
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # =========================
    # Debug Helper
    # =========================
    def __repr__(self) -> str:
        return (
            f"<Step3ExecutionControl("
            f"trade_date={self.trade_date}, "
            f"market_context={self.market_context}, "
            f"trade_permission={self.trade_permission}, "
            f"execution_allowed={self.execution_allowed}"
            f")>"
        )
