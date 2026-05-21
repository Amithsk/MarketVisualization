#IntradayTradeStockAnalyser/backend/services/normalization_service.py
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
    def filter_required_columns(cls,dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Keep ONLY replay-required columns.
        Ignore everything else.
        """

        missing_columns = [
            column
            for column in cls.REQUIRED_FIELDS
            if column not in dataframe.columns
            ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: "
                f"{missing_columns}"
            )

        return dataframe[cls.REQUIRED_FIELDS]
    

    @classmethod
    def normalize_candles(cls, dataframe: pd.DataFrame) -> List[Candle]:
        """
        Convert dataframe rows into standardized Candle objects.
        """

        dataframe = cls.normalize_columns(dataframe)

        dataframe = cls.filter_required_columns(dataframe)

        candles = []

        for _, row in dataframe.iterrows():

            # -----------------------------------
            # Normalize timestamp
            # -----------------------------------

            normalized_time = cls.clean_time(row.get("time", ""))

            # -----------------------------------
            # Skip candles outside market hours
            # Example:
            # 15:20 candle
            # -----------------------------------

            if not cls.is_market_hours(normalized_time):
                continue

            # -----------------------------------
            # Create standardized candle
            # -----------------------------------

            candle = Candle.from_dict({

                "time": normalized_time,

                "open": cls.clean_numeric(
                row.get("open", 0)
                     ),

                "high": cls.clean_numeric(
                row.get("high", 0)
                    ),

                "low": cls.clean_numeric(
                row.get("low", 0)
                    ),

                "close": cls.clean_numeric(
                row.get("close", 0)
                    ),

                "volume": cls.clean_numeric(
                    row.get("volume", 0)
                )

            })

            candles.append(candle)
        candles.sort(key=lambda candle: candle.time)

        return candles
    
    @staticmethod
    def clean_numeric(value):
        """
        Clean numeric fields.

        Handles:
        - commas
        - empty strings
        - NaN
        """
        if pd.isna(value):
            return 0

        value = str(value).strip()

        # Remove commas
        value = value.replace(",", "")

        if value == "":
            return 0

        return float(value)
    
    @staticmethod
    def clean_time(value):
        """
        Normalize different broker timestamp formats
        into standard replay format.

        Final format:
        YYYY-MM-DD HH:MM:SS
        """

        if pd.isna(value):
            return ""

        value = str(value).strip()

        try:

            # -----------------------------------
            # Remove browser timezone text
            # Example:
            # GMT+0530 (India Standard Time)
            # -----------------------------------

            if "GMT" in value:

                value = value.split("GMT")[0].strip()

            # -----------------------------------
            # Parse cleaned timestamp
            # -----------------------------------

            parsed = pd.to_datetime(value)

            return parsed.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except Exception as error:

            raise ValueError(f"Unsupported timestamp format: "
            f"{value} | Error: {str(error)}"
                    )
        
    @staticmethod
    def is_market_hours(timestamp):
        """
         Keep only valid intraday market candles.
        """

        parsed = pd.to_datetime(timestamp)

        candle_time = parsed.strftime("%H:%M")

        return (
          candle_time >= "09:15"
          and candle_time <= "15:15"
             )