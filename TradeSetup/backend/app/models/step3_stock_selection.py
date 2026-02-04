# backend/app/models/step3_stock_selection.py

from sqlalchemy import Column, Date, String, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Step3StockSelection(Base):
    """
    STEP-3: Stock Selection
    -----------------------
    Stores system-generated, read-only trade candidates
    for a given trading day.
    """

    __tablename__ = "step3_stock_selection"

    # Identity
    trade_date = Column(Date, primary_key=True, index=True)
    symbol = Column(String(32), primary_key=True)

    # Execution direction (LONG / SHORT)
    direction = Column(String(16), nullable=False)

    # High-level setup classification
    setup_type = Column(String(32), nullable=False)

    # Optional system notes
    notes = Column(String(256), nullable=True)

    # Audit
    created_at = Column(DateTime, server_default=func.now(), nullable=False)