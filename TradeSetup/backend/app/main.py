# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# -------------------------------
# IMPORTANT: Import ALL models
# Ensures SQLAlchemy registers them
# -------------------------------
from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step2_market_open_behavior import Step2MarketOpenBehavior
from backend.app.models.step3_execution_control import Step3ExecutionControl
from backend.app.models.step3_stock_selection import Step3StockSelection
from backend.app.models.step4_trade import Step4Trade

from backend.app.api.step1 import router as step1_router
from backend.app.api.step2 import router as step2_router
from backend.app.api.step3 import router as step3_router
from backend.app.api.step4 import router as step4_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="TradeSetup Backend")

# -------------------------------------------------
# CORS (required for Next.js frontend)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# API Routers
# -------------------------------------------------
app.include_router(step1_router)
app.include_router(step2_router)
app.include_router(step3_router)
app.include_router(step4_router)
