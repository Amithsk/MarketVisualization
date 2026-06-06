from datetime import datetime
from typing import List

from backend.models.candle_model import Candle


class CandleValidator:

    MARKET_START = "09:15"
    MARKET_END = "15:15"

    REQUIRED_FIELDS = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    @classmethod
    def validate_required_fields(cls, candle: Candle):

        missing_fields = []

        for field in cls.REQUIRED_FIELDS:

            value = getattr(candle, field)

            if value is None or value == "":
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                f"Missing required fields: {missing_fields}"
            )

    @classmethod
    def validate_ohlc(cls, candle: Candle):

        if candle.high < candle.open:
            raise ValueError(
                f"Invalid candle: HIGH < OPEN at {candle.time}"
            )

        if candle.high < candle.close:
            raise ValueError(
                f"Invalid candle: HIGH < CLOSE at {candle.time}"
            )

        if candle.low > candle.open:
            raise ValueError(
                f"Invalid candle: LOW > OPEN at {candle.time}"
            )

        if candle.low > candle.close:
            raise ValueError(
                f"Invalid candle: LOW > CLOSE at {candle.time}"
            )

    @classmethod
    def validate_volume(cls, candle: Candle):

        if candle.volume < 0:
            raise ValueError(
                f"Negative volume detected at {candle.time}"
            )

    @classmethod
    def validate_market_time(cls, candle: Candle):

        try:
            parsed_time = datetime.strptime(
                candle.time,
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            raise ValueError(
                f"Invalid time format: {candle.time}"
            )

        candle_time = parsed_time.strftime("%H:%M")

        if candle_time < cls.MARKET_START:
            raise ValueError(
                f"Candle before market open: {candle.time}"
            )

        if candle_time > cls.MARKET_END:
            raise ValueError(
                f"Candle after market close: {candle.time}"
            )

    @classmethod
    def validate_duplicate_timestamps(
        cls,
        candles: List[Candle]
    ):

        timestamps = set()

        for candle in candles:

            if candle.time in timestamps:
                raise ValueError(
                    f"Duplicate timestamp found: {candle.time}"
                )

            timestamps.add(candle.time)

    @classmethod
    def validate_5_minute_intervals(
        cls,
        candles: List[Candle]
    ):

        sorted_candles = sorted(
            candles,
            key=lambda x: x.time
        )

        previous_time = None

        for candle in sorted_candles:

            current_time = datetime.strptime(
                candle.time,
                "%Y-%m-%d %H:%M:%S"
            )

            if previous_time:

                difference = (
                    current_time - previous_time
                ).seconds / 60

                if difference != 5:
                    raise ValueError(
                        f"Invalid interval between "
                        f"{previous_time} and {current_time}"
                    )

            previous_time = current_time

    @classmethod
    def validate_candles(
        cls,
        candles: List[Candle]
    ):

        if not candles:
            raise ValueError("No candle data found")

        for candle in candles:

            cls.validate_required_fields(candle)

            cls.validate_ohlc(candle)

            cls.validate_volume(candle)

            cls.validate_market_time(candle)

        cls.validate_duplicate_timestamps(candles)

        cls.validate_5_minute_intervals(candles)

        return True