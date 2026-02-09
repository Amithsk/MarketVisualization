import logging
from datetime import date, datetime
from typing import Optional, Literal, List, Dict
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


# =========================
# Requests
# =========================

class Step1PreviewRequest(BaseModel):
    trade_date: date

    @model_validator(mode="after")
    def log_preview_request(self):
        logger.debug(
            "[STEP-1][SCHEMA][PREVIEW_REQUEST] trade_date=%s",
            self.trade_date,
        )
        return self


class Step1ComputeRequest(BaseModel):
    """
    MANUAL MODE ONLY
    Raw inputs provided by trader.
    """

    yesterday_close: float
    yesterday_high: float
    yesterday_low: float

    day2_high: float
    day2_low: float

    last_5_day_ranges: List[float] = Field(
        ...,
        min_items=3,
        description="Most recent → oldest daily ranges",
    )

    preopen_price: float

    @model_validator(mode="after")
    def log_compute_request(self):
        logger.debug(
            "[STEP-1][SCHEMA][COMPUTE_REQUEST] yc=%s yh=%s yl=%s d2h=%s d2l=%s preopen=%s ranges=%s",
            self.yesterday_close,
            self.yesterday_high,
            self.yesterday_low,
            self.day2_high,
            self.day2_low,
            self.preopen_price,
            self.last_5_day_ranges,
        )
        return self


class Step1FreezeRequest(BaseModel):
    trade_date: date

    market_bias: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Trader view of market bias",
    )

    gap_context: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="System or trader-confirmed gap direction",
    )

    premarket_notes: Optional[str] = Field(
        None,
        max_length=1000,
    )

    @model_validator(mode="after")
    def log_freeze_request(self):
        logger.debug(
            "[STEP-1][SCHEMA][FREEZE_REQUEST] trade_date=%s market_bias=%s gap_context=%s notes_present=%s",
            self.trade_date,
            self.market_bias,
            self.gap_context,
            self.premarket_notes is not None,
        )
        return self


# =========================
# Snapshot
# =========================

class Step1ContextSnapshot(BaseModel):
    trade_date: date

    yesterday_close: Optional[float] = None
    yesterday_high: Optional[float] = None
    yesterday_low: Optional[float] = None

    last_5_day_ranges: List[float] = []

    market_bias: Optional[str] = None
    gap_context: Optional[str] = None
    premarket_notes: Optional[str] = None

    frozen_at: Optional[datetime] = None

    @model_validator(mode="after")
    def log_snapshot(self):
        logger.debug(
            "[STEP-1][SCHEMA][SNAPSHOT] trade_date=%s frozen=%s yc=%s yh=%s yl=%s ranges=%s bias=%s gap=%s",
            self.trade_date,
            self.frozen_at is not None,
            self.yesterday_close,
            self.yesterday_high,
            self.yesterday_low,
            self.last_5_day_ranges,
            self.market_bias,
            self.gap_context,
        )
        return self

    class Config:
        from_attributes = True


# =========================
# Responses
# =========================

class Step1PreviewResponse(BaseModel):
    mode: Literal["AUTO", "MANUAL"]
    snapshot: Step1ContextSnapshot
    can_freeze: bool

    @model_validator(mode="after")
    def log_preview_response(self):
        logger.debug(
            "[STEP-1][SCHEMA][PREVIEW_RESPONSE] mode=%s can_freeze=%s frozen=%s",
            self.mode,
            self.can_freeze,
            self.snapshot.frozen_at is not None,
        )
        return self


class Step1ComputeResponse(BaseModel):
    """
    Returned only by /compute
    """

    derived_context: Dict[str, float | str]
    suggested_market_context: Literal[
        "TREND_DAY",
        "RANGE_UNCERTAIN_DAY",
        "NO_TRADE_DAY",
    ]

    @model_validator(mode="after")
    def validate_and_log_compute_response(self):
        if "gap_context" not in self.derived_context:
            logger.warning(
                "[STEP-1][SCHEMA][COMPUTE_RESPONSE] gap_context MISSING in derived_context=%s",
                self.derived_context,
            )
        else:
            logger.debug(
                "[STEP-1][SCHEMA][COMPUTE_RESPONSE] gap_context=%s",
                self.derived_context.get("gap_context"),
            )

        logger.debug(
            "[STEP-1][SCHEMA][COMPUTE_RESPONSE] derived=%s suggested_context=%s",
            self.derived_context,
            self.suggested_market_context,
        )
        return self


class Step1FrozenResponse(BaseModel):
    snapshot: Step1ContextSnapshot
    frozen: bool = True

    @model_validator(mode="after")
    def log_frozen_response(self):
        logger.debug(
            "[STEP-1][SCHEMA][FROZEN_RESPONSE] trade_date=%s frozen=%s bias=%s gap=%s",
            self.snapshot.trade_date,
            self.frozen,
            self.snapshot.market_bias,
            self.snapshot.gap_context,
        )
        return self
