#IntradayTradeNiftyAnalyser/backend/app/repositories/analytics/performance_repository.py

from sqlalchemy.orm import Session

from backend.app.repositories.analytics.performance_repository import (
    PerformanceRepository,
)


class PerformanceService:
    """
    ====================================================
    PERFORMANCE SERVICE

    Purpose:
        Assemble STEP 3 performance response.

    Sources:
        PerformanceRepository

    Responsibilities:
        - Fetch repository data
        - Assemble response payload

    Must NOT:
        - Calculate conversion rates
        - Calculate failure rates
        - Calculate missed opportunities
        - Generate suggestions
        - Generate learning
    ====================================================
    """

    def __init__(self, db: Session):
        self.repository = PerformanceRepository(db)

    def get_performance(
        self,
        trade_date: str,
    ):
        """
        Used By:
            GET /api/analytics/performance/{trade_date}
        """

        execution_control = (
            self.repository.get_execution_control(
                trade_date
            )
        )

        stock_selection = (
            self.repository.get_stock_selection(
                trade_date
            )
        )

        performance_metrics = (
            self.repository.get_stock_insights(
                trade_date
            )
        )

        return {
            "trade_date": trade_date,
            "execution_control": execution_control,
            "stock_selection": stock_selection,
            "performance_metrics": performance_metrics,
        }