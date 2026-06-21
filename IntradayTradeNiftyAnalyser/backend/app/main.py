#IntradayTradeNiftyAnalyser/backend/app/main.py

from fastapi import FastAPI

from backend.app.api.analytics.step1 import (
    router as analytics_step1_router,
)

from backend.app.api.analytics.step2 import (
    router as analytics_step2_router,
)


from backend.app.api.analytics.performance import (
    router as analytics_performance_router,
)

from backend.app.api.analytics.learning import (
    router as analytics_learning_router,
)

app = FastAPI(
    title="NIFTY Analytics API",
    version="1.0.0",
)

app.include_router(
    analytics_step1_router
)

app.include_router(
    analytics_step2_router
)

app.include_router(
    analytics_performance_router
)

app.include_router(
    analytics_learning_router
)