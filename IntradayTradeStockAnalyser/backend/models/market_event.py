# IntradayTradeStockAnalyser/backend/models/market_event.py

from dataclasses import dataclass
from typing import Optional

from constants.event_types import EventType


@dataclass
class NiftyContext:
    direction: str
    relative_strength_score: float


@dataclass
class EventValidation:
    above_vwap: bool
    volume_expansion: bool
    orb_valid: bool


@dataclass
class MarketEvent:
    id: str

    symbol: str

    event_type: EventType

    timestamp: str

    candle_index: int

    price: float

    strength_score: float

    nifty_context: NiftyContext

    validation: EventValidation

    explanation: str

    trading_implication: str

    event_metadata: Optional[dict] = None