#IntradayTradeNiftyAnalyser/backend/app/repositories/analytics/step1_repository.py
from sqlalchemy.orm import Session

from backend.app.repositories.analytics.step1_repository import (
    Step1Repository,
)


class Step1Service:
    """
    ====================================================
    STEP 1 SERVICE

    Purpose:
        Assemble STEP 1 response for API layer.

    Sources:
        Step1Repository

    Responsibilities:
        - Fetch repository data
        - Assemble response structure

    Must NOT:
        - Calculate analytics
        - Generate learning
        - Generate pass/fail
        - Recompute market classifications
    ====================================================
    """

    def __init__(self, db: Session):
        self.repository = Step1Repository(db)

    def get_step1_validation(
        self,
        trade_date: str,
    ):
        """
        Returns STEP 1 validation payload.

        Used by:
            GET /api/analytics/step1/{trade_date}
        """

        step1_context = self.repository.get_step1_context(
            trade_date
        )

        nifty_validation = self.repository.get_nifty_validation(
            trade_date
        )

        return {
            "trade_date": trade_date,
            "step1_context": step1_context,
            "market_validation": nifty_validation,
        }