#IntradayTradeNiftyAnalyser/backend/app/repositories/analytics/step2_repository.py

from sqlalchemy.orm import Session

from backend.app.repositories.analytics.step2_repository import (
    Step2Repository,
)


class Step2Service:
    """
    ====================================================
    STEP 2 SERVICE

    Purpose:
        Assemble STEP 2 validation response.

    Sources:
        Step2Repository

    UI Section:
        STEP 2 VALIDATION

    Responsibilities:
        - Fetch repository data
        - Assemble response payload

    Must NOT:
        - Calculate analytics
        - Generate learning
        - Generate pass/fail
        - Compare system vs market
        - Recompute trend strength
        - Recompute VWAP statistics

    Analytical Engine remains the source of truth.
    ====================================================
    """

    def __init__(self, db: Session):
        self.repository = Step2Repository(db)

    def get_step2_validation(
        self,
        trade_date: str,
    ):
        """
        ====================================================
        STEP 2 VALIDATION

        Used By:
            GET /api/analytics/step2/{trade_date}

        Response Structure:

        {
            "trade_date": "...",

            "market_behavior": {},

            "market_open_behavior": {},

            "market_validation": {}
        }
        ====================================================
        """

        market_behavior = (
            self.repository.get_market_behavior(
                trade_date
            )
        )

        market_open_behavior = (
            self.repository.get_market_open_behavior(
                trade_date
            )
        )

        market_validation = (
            self.repository.get_vwap_validation(
                trade_date
            )
        )

        return {
            "trade_date": trade_date,
            "market_behavior": market_behavior,
            "market_open_behavior": market_open_behavior,
            "market_validation": market_validation,
        }