#IntradayTradeStockAnalyser/backend/app.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.upload import (router as upload_router)

from backend.api.trades import ( router as trades_router)

from backend.api.nifty import (router as nifty_router)
from backend.api.replay import (  router as replay_router)
from backend.api.live import (router as live_router)
from fastapi.middleware.cors import (    CORSMiddleware)
from backend.services.live_nifty_poller import LiveNiftyPoller
from backend.services.replay_stock_fetch_service import ReplayStockFetchService


@asynccontextmanager
async def lifespan(app: FastAPI):

    ReplayStockFetchService.log_market_data_configuration()
    LiveNiftyPoller.start()

    try:
        yield
    finally:
        await LiveNiftyPoller.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(upload_router)

app.include_router(replay_router)

app.include_router(trades_router)

app.include_router(nifty_router)
app.include_router(live_router)
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
