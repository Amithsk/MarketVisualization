from datetime import datetime
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("Asia/Kolkata")


def to_market_time(value: datetime) -> datetime:
    """Interpret naïve values as India market time and convert aware values to it."""
    if value.tzinfo is None:
        return value.replace(tzinfo=MARKET_TIMEZONE)
    return value.astimezone(MARKET_TIMEZONE)


def to_storage_time(value: datetime) -> datetime:
    """Store India market wall time in the existing timezone-less MySQL DATETIME."""
    return to_market_time(value).replace(tzinfo=None)


def to_api_time(value: datetime | None) -> str | None:
    """Return a stored market wall time with the explicit Asia/Kolkata offset."""
    if value is None:
        return None
    return to_market_time(value).isoformat()
