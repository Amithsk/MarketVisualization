#IntradayTradeStockAnalyser/backend/api/upload.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

import os
import shutil
import uuid

from  backend.services.upload_service import UploadService


router = APIRouter()

UPLOAD_DIRECTORY = "uploads"

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


@router.post("/api/v1/upload/stock-candles")
async def upload_stock_candles(
    file: UploadFile = File(...)
):
    """
    Upload stock candle CSV/Excel file.

    Flow:
    - Save uploaded file
    - Normalize candles
    - Validate candles
    - Return replay-ready response
    """

    try:

        # -----------------------------------
        # DEBUG STEP 1
        # -----------------------------------
        print("\n========== FILE UPLOAD STARTED ==========")

        print(f"Uploaded filename: {file.filename}")

        # -----------------------------------
        # Generate unique filename
        # -----------------------------------

        unique_filename = (
            f"{uuid.uuid4()}_{file.filename}"
        )

        saved_path = os.path.join(
            UPLOAD_DIRECTORY,
            unique_filename
        )

        # -----------------------------------
        # Save uploaded file
        # -----------------------------------

        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -----------------------------------
        # DEBUG STEP 2
        # -----------------------------------
        print(f"File saved at: {saved_path}")

        # -----------------------------------
        # Process upload pipeline
        # -----------------------------------

        candles = UploadService.process_upload(
            saved_path
        )

        # -----------------------------------
        # DEBUG STEP 3
        # -----------------------------------
        print(
            f"Total normalized candles: "
            f"{len(candles)}"
        )

        # -----------------------------------
        # DEBUG STEP 4
        # Print first candle
        # -----------------------------------

        if candles:

            print("First candle:")

            print(candles[0].to_dict())

        print("========== FILE UPLOAD SUCCESS ==========\n")

        # -----------------------------------
        # API Response
        # -----------------------------------

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "File uploaded successfully",
                "total_candles": len(candles),
                "candles": [
                    candle.to_dict()
                    for candle in candles[:5]
                ]
            }
        )

    except Exception as error:

        # -----------------------------------
        # DEBUG STEP 5
        # -----------------------------------

        print("\n========== FILE UPLOAD FAILED ==========")

        print(str(error))

        print("========================================\n")

        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(error)
            }
        )