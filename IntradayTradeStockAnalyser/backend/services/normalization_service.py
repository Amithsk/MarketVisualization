import pandas as pd
from typing import List

from models.candle_model import Candle


class NormalizationService:
    """
    Responsible for converting uploaded candle files
    into standardized replay candle structure.
    """

    # Supported column aliases
    COLUMN_MAPPINGS = {
        "time": ["time", "timestamp", "date", "datetime"],
        "open": ["open", "o"],
        "high": ["high", "h"],
        "low": ["low", "l"],
        "close": ["close", "c"],
        "volume": ["volume", "vol", "volume traded"]
    }

    REQUIRED_FIELDS = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    @classmethod
    def normalize_columns(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names.

        Extra columns are ignored automatically.
        """

        normalized_columns = {}

        for column in dataframe.columns:

            clean_column = str(column).strip().lower()

            matched = False

            for standard_name, aliases in cls.COLUMN_MAPPINGS.items():

                if clean_column in aliases:
                    normalized_columns[column] = standard_name
                    matched = True
                    break

            # Ignore unknown columns completely
            if not matched:
                continue

        dataframe = dataframe.rename(columns=normalized_columns)

        return dataframe

    @classmethod
    def filter_required_columns(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Keep ONLY replay-required columns.
        Ignore everything else.
        """

        available_columns = [
            column
            for column in cls.REQUIRED_FIELDS
            if column in dataframe.columns
        ]

        return dataframe[available_columns]

    @classmethod
    def normalize_candles(cls, dataframe: pd.DataFrame) -> List[Candle]:
        """
        Convert dataframe rows into standardized Candle objects.
        """

        dataframe = cls.normalize_columns(dataframe)

        dataframe = cls.filter_required_columns(dataframe)

        candles = []

        for _, row in dataframe.iterrows():

            candle = Candle.from_dict({
                "time": str(row.get("time", "")),
                "open": row.get("open", 0),
                "high": row.get("high", 0),
                "low": row.get("low", 0),
                "close": row.get("close", 0),
                "volume": row.get("volume", 0)
            })

            candles.append(candle)

        return candles