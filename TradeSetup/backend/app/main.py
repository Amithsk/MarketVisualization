from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.step1 import router as step1_router
from backend.app.api.step2 import router as step2_router
from backend.app.api.step3 import router as step3_router
from backend.app.api.step4 import router as step4_router

app = FastAPI(title="TradeSetup Backend")

# REQUIRED: allow frontend (browser) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],         # allows OPTIONS, POST, etc.
    allow_headers=["*"],
)

# API routers
app.include_router(step1_router, prefix="/api/step1", tags=["STEP-1"])
app.include_router(step2_router, prefix="/api/step2", tags=["STEP-2"])
app.include_router(step3_router, prefix="/api/step3", tags=["STEP-3"])
app.include_router(step4_router, prefix="/api/step4", tags=["STEP-4"])
