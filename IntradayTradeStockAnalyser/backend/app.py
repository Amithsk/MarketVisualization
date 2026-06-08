#IntradayTradeStockAnalyser/backend/app.py
from fastapi import FastAPI

from backend.api.upload import (router as upload_router)

from backend.api.trades import ( router as trades_router)

from backend.api.nifty import (router as nifty_router)
from backend.api.replay import (  router as replay_router)
from fastapi.middleware.cors import (    CORSMiddleware)
app = FastAPI()

app.include_router(upload_router)

app.include_router(replay_router)

app.include_router(trades_router)

app.include_router(nifty_router)
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3003"
    ],


    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)