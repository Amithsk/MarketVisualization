# backend/app/models/step3_execution_control.py

from sqlalchemy import Column, Date, Boolean, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3ExecutionControl(Base):
    """
    STEP-3: Execution Control
    -------------------------
    Stores whether execution was enabled for the day
    and when STEP-3 was generated.
    """

    __tablename__ = "step3_execution_control"

    # Identity
    trade_date = Column(Date, primary_key=True, index=True)

    # Whether STEP-3 was enabled (depends on STEP-1 & STEP-2)
    execution_enabled = Column(Boolean, nullable=False)

    # When STEP-3 was generated
    generated_at = Column(DateTime, server_default=func.now(), nullable=False)