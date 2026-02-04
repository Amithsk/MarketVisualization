# backend/app/main.py

from fastapi import FastAPI


from backend.app.api.step1 import router as step1_router
from backend.app.api.step2 import router as step2_router
# Register routers

app = FastAPI(title="TradeSetup Backend")
app.include_router(step1_router)
app.include_router(step2_router)