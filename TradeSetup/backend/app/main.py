from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.step1 import router as step1_router
from backend.app.api.step2 import router as step2_router
from backend.app.api.step3 import router as step3_router
from backend.app.api.step4 import router as step4_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="TradeSetup Backend")

# -------------------------------------------------
# CORS (required for Next.js frontend)
# IMPORTANT:
# Allow BOTH localhost and 127.0.0.1
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
# IMPORTANT:
# Routers ALREADY define their own prefixes
# DO NOT re-prefix them here
# -------------------------------------------------
app.include_router(step1_router)
app.include_router(step2_router)
app.include_router(step3_router)
app.include_router(step4_router)
