from fastapi import FastAPI

from backend.api.upload import (
    router as upload_router
)

from backend.api.trades import (
    router as trades_router
)

app = FastAPI()

app.include_router(upload_router)

app.include_router(trades_router)