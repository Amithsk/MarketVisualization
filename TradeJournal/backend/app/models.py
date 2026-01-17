# app/models.py
from sqlalchemy import Computed
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    Date,
    DateTime,
    DECIMAL,
    Text,
    ForeignKey,
    Integer,
    JSON,
    TIMESTAMP,
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

# --------------------------------------------------
# ENUMS (MATCH DB EXACTLY)
# --------------------------------------------------

class PlanStatus(enum.Enum):
    PLANNED = "PLANNED"
    EXECUTED = "EXECUTED"
    NOT_TAKEN = "NOT_TAKEN"


class TradeSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeSource(enum.Enum):
    auto = "auto"
    manual = "manual"
    sim = "sim"


class TradeStatus(enum.Enum):
    sent = "sent"
    filled = "filled"
    partially_filled = "partially_filled"
    cancelled = "cancelled"
    rejected = "rejected"


class PositionType(enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"


# --------------------------------------------------
# TRADE PLAN
# Table: intradaytrading.trade_plan
# --------------------------------------------------

class TradePlan(Base):
    __tablename__ = "trade_plan"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    trade_id = Column(
        BigInteger,
        ForeignKey("trade_log.id"),
        unique=True,
        nullable=True,
    )

    plan_date = Column(Date, nullable=False)
    trade_mode = Column(Enum("PAPER", "REAL"), nullable=False)
    strategy = Column(String(64), nullable=False)
    position_type = Column(Enum("LONG", "SHORT"), nullable=False)

    setup_description = Column(Text, nullable=False)
    entry_trigger = Column(String(64), nullable=True)

    planned_entry_price = Column(DECIMAL(18, 6), nullable=False)
    planned_stop_price = Column(DECIMAL(18, 6), nullable=False)
    planned_target_price = Column(DECIMAL(18, 6), nullable=True)
    planned_risk_amount = Column(DECIMAL(18, 2), nullable=False)
    planned_position_size = Column(BigInteger, nullable=False)

    plan_status = Column(
        Enum(PlanStatus),
        nullable=False,
        default=PlanStatus.PLANNED,
    )

    not_taken_reason = Column(String(128), nullable=True)

    created_at = Column(
        TIMESTAMP,
        nullable=True,
        server_default="CURRENT_TIMESTAMP",
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=True,
        server_default="CURRENT_TIMESTAMP",
        server_onupdate="CURRENT_TIMESTAMP",
    )

    # ✅ ONE-WAY relationship ONLY (no back_populates)
    trade = relationship("TradeLog", uselist=False)


# --------------------------------------------------
# TRADE LOG
# Table: intradaytrading.trade_log
# --------------------------------------------------

class TradeLog(Base):
    __tablename__ = "trade_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    timestamp = Column(DateTime, nullable=False)

    symbol = Column(String(32), nullable=False)
    order_id = Column(String(128), nullable=True)

    side = Column(Enum(TradeSide), nullable=False)
    quantity = Column(BigInteger, nullable=False)

    price = Column(DECIMAL(18, 6), nullable=False)
    executed_amount = Column(DECIMAL(24, 6), nullable=True)

    order_type = Column(String(32), nullable=True)
    strategy = Column(String(64), nullable=True)
    signal_score = Column(DECIMAL(8, 6), nullable=True)

    source = Column(
        Enum(TradeSource),
        nullable=False,
        default=TradeSource.auto,
    )

    status = Column(
        Enum(TradeStatus),
        nullable=False,
        default=TradeStatus.sent,
    )

    entry_price = Column(DECIMAL(18, 6), nullable=True)
    exit_price = Column(DECIMAL(18, 6), nullable=True)
    exit_timestamp = Column(DateTime, nullable=True)
    fees = Column(DECIMAL(18, 6), nullable=True)

    exit_reason = Column(String(128), nullable=True)

    instrument_type = Column(String(32), nullable=True)
    position_type = Column(Enum(PositionType), nullable=True)
    trade_tag = Column(String(64), nullable=True)

    # --------------------------------------------------
    # GENERATED COLUMNS — DO NOT WRITE FROM ORM
    # (MySQL STORED GENERATED)
    # --------------------------------------------------

    pnl_amount = Column(
        DECIMAL(24, 6),
        Computed("pnl_amount"),
        nullable=True,
    )

    pnl_pct = Column(
        DECIMAL(9, 4),
        Computed("pnl_pct"),
        nullable=True,
    )

    trade_result = Column(
        Enum("profit", "loss", "breakeven", "open", "cancelled"),
        Computed("trade_result"),
        nullable=True,
    )

    duration_seconds = Column(
        Integer,
        Computed("duration_seconds"),
        nullable=True,
    )

    notes = Column(JSON, nullable=True)

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        server_onupdate="CURRENT_TIMESTAMP",
    )


# --------------------------------------------------
# TRADE EXECUTION REVIEW
# Table: intradaytrading.trade_execution_review
# --------------------------------------------------

class TradeExecutionReview(Base):
    __tablename__ = "trade_execution_review"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    trade_id = Column(
        BigInteger,
        ForeignKey("trade_log.id"),
        unique=True,
        nullable=False,
    )

    exit_reason = Column(
        Enum(
            "STOP_HIT",
            "TARGET_HIT",
            "TRAILING_STOP",
            "MANUAL_FEAR",
            "MANUAL_CONFUSION",
            "RULE_VIOLATION",
        ),
        nullable=False,
    )

    followed_entry_rules = Column(Integer, nullable=False)
    followed_stop_rules = Column(Integer, nullable=False)
    followed_position_sizing = Column(Integer, nullable=False)

    emotional_state = Column(
        Enum(
            "CALM",
            "HESITANT",
            "FEARFUL",
            "CONFIDENT",
            "FOMO",
            "REVENGE",
            "DISTRACTED",
        ),
        nullable=False,
    )

    market_context = Column(
        Enum(
            "TRENDING",
            "RANGE",
            "CHOPPY",
            "NEWS_DRIVEN",
            "LOW_LIQUIDITY",
        ),
        nullable=False,
    )

    learning_insight = Column(Text, nullable=False)
    trade_grade = Column(Enum("A", "B", "C"), nullable=False)

    reviewed_at = Column(
        TIMESTAMP,
        nullable=True,
        server_default="CURRENT_TIMESTAMP",
    )

    # ONE-WAY relationship
    trade = relationship("TradeLog", uselist=False)
