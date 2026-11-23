from typing import Optional

from pydantic import BaseModel, Field


class StockIdentitySchema(BaseModel):
    exchange: str
    symbol: str


class AvailabilitySchema(BaseModel):
    state: str
    reason: Optional[str] = None


class ZoneSchema(AvailabilitySchema):
    level: Optional[float] = None
    lower: Optional[float] = None
    upper: Optional[float] = None
    confirmation: Optional[str] = None
    rule: Optional[str] = None
    reaction_timestamps: list[str] = Field(default_factory=list)


class MovementSchema(BaseModel):
    label: Optional[str] = None
    points: Optional[float] = None
    percent: Optional[float] = None
    explanation: Optional[str] = None
    key_observations: list[dict] = Field(default_factory=list)


class VolumeContextSchema(AvailabilitySchema):
    comparison: Optional[str] = None
    bounce_volume: Optional[float] = None
    prior_five_median_volume: Optional[float] = None
    bounce_timestamp: Optional[str] = None
    schema_version: Optional[str] = None


class HeaderSchema(BaseModel):
    exchange: str
    symbol: str
    trade_date: str
    candle_interval_minutes: Optional[int] = None
    timezone: Optional[str] = None


class SessionSchema(BaseModel):
    open: float
    high: float
    low: float
    close: float
    move_points: Optional[float] = None
    move_percent: Optional[float] = None


class BenchmarkMoveSchema(BaseModel):
    open: Optional[float] = None
    close: Optional[float] = None
    points: Optional[float] = None
    percent: Optional[float] = None


class BenchmarkSchema(AvailabilitySchema):
    benchmark_status: str
    identity: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[str] = None
    interval_start: Optional[str] = None
    interval_end: Optional[str] = None
    stock: Optional[BenchmarkMoveSchema] = None
    benchmark: Optional[BenchmarkMoveSchema] = None
    relationship: Optional[str] = None
    explanation: Optional[str] = None
    reference_timestamp: Optional[str] = None
    coverage: Optional[dict] = None


class ScenarioSchema(AvailabilitySchema):
    condition: Optional[str] = None
    zone: Optional[dict] = None


class NextSessionWatchSchema(BaseModel):
    schema_version: Optional[str] = None
    support_scenario: Optional[ScenarioSchema] = None
    resistance_scenario: Optional[ScenarioSchema] = None


class StockReviewResponseSchema(BaseModel):
    header: HeaderSchema
    status: str
    analysis_version: str
    session: SessionSchema
    movement: Optional[MovementSchema] = None
    support: ZoneSchema
    resistance: ZoneSchema
    benchmark: BenchmarkSchema
    volume_context: VolumeContextSchema
    next_session_watch: NextSessionWatchSchema
