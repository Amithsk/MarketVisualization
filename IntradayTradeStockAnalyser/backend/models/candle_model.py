from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Candle:
    """
    Standard normalized candle structure
    used across the entire replay system.

    ALL uploaded candle formats
    must be converted into this structure.
    """

    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert candle object to dictionary.
        Useful for API responses and JSON serialization.
        """
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Candle":
        """
        Create Candle object from dictionary.

        IMPORTANT:
        Extra fields are ignored automatically.
        Only required replay fields are extracted.
        """

        return Candle(
            time=str(data.get("time", "")),
            open=float(data.get("open", 0)),
            high=float(data.get("high", 0)),
            low=float(data.get("low", 0)),
            close=float(data.get("close", 0)),
            volume=float(data.get("volume", 0)),
            vwap=float(data.get("vwap", 0))
        )