# Main to control
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import trade_plans, trades, calendar  

app = FastAPI(title="Trade Journal API")

# --------------------------------------------------
# CORS (MANDATORY FOR FRONTEND)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Routers
# --------------------------------------------------
app.include_router(trade_plans.router)
app.include_router(trades.router)
app.include_router(calendar.router)  # ✅ REGISTER calendar route
