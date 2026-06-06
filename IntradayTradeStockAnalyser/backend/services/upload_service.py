import pandas as pd
from typing import List

from backend.models.candle_model import Candle
from backend.services.normalization_service import NormalizationService
from backend.validators.candle_validator import CandleValidator
from backend.utils.replay_store import (ReplayStore)


class UploadService:
    """
    Handles uploaded stock candle files.

    Responsibilities:
    - Read CSV/Excel
    - Normalize candle structure
    - Validate candles
    - Return replay-ready candles
    """

    SUPPORTED_EXTENSIONS = [
        ".csv",
        ".xlsx",
        ".xls"
    ]

    @classmethod
    def validate_file_extension(cls, file_name: str):

        file_name = file_name.lower()

        if not any(
            file_name.endswith(ext)
            for ext in cls.SUPPORTED_EXTENSIONS
        ):
            raise ValueError(
                f"Unsupported file type: {file_name}"
            )

    @classmethod
    def read_file(
        cls,
        file_path: str
    ) -> pd.DataFrame:
        """
        Read uploaded CSV or Excel file.
        """

        lower_path = file_path.lower()

        try:

            if lower_path.endswith(".csv"):
                dataframe = pd.read_csv(file_path)

            elif (
                lower_path.endswith(".xlsx")
                or lower_path.endswith(".xls")
            ):
                dataframe = pd.read_excel(file_path)

            else:
                raise ValueError(
                    "Unsupported file format"
                )

            return dataframe

        except Exception as error:

            raise ValueError(
                f"Failed to read uploaded file: {str(error)}"
            )

    @classmethod
    def process_upload(
        cls,
        file_path: str
    ) -> List[Candle]:
        """
        Complete upload pipeline.

        Flow:
        - Validate extension
        - Read file
        - Normalize candles
        - Validate candles
        - Return replay-ready candles
        """

        cls.validate_file_extension(file_path)

        dataframe = cls.read_file(file_path)

        candles = (
            NormalizationService
            .normalize_candles(dataframe)
        )

        CandleValidator.validate_candles(candles)

        # -----------------------------------
        # Store replay candles in memory
        # for replay API usage
        # -----------------------------------

        ReplayStore.set_stock_candles(candles)

        return candles