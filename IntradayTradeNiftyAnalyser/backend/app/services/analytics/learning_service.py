#IntradayTradeNiftyAnalyser/backend/app/repositories/analytics/learning_repository.py

from sqlalchemy.orm import Session

from backend.app.repositories.analytics.learning_repository import (
    LearningRepository,
)


class LearningService:
    """
    ====================================================
    LEARNING SERVICE

    Purpose:
        Assemble learning response.

    Sources:
        LearningRepository

    Responsibilities:
        - Fetch repository data
        - Assemble response payload

    Must NOT:
        - Generate learning
        - Generate suggestions
        - Generate summaries
        - Calculate metrics

    Analytical Engine remains the source of truth.
    ====================================================
    """

    def __init__(self, db: Session):
        self.repository = LearningRepository(db)

    def get_learning(
        self,
        trade_date: str,
    ):
        """
        Used By:
            GET /api/analytics/learning/{trade_date}
        """

        summary = self.repository.get_summary(
            trade_date
        )

        suggestions = self.repository.get_suggestions(
            trade_date
        )

        job_status = self.repository.get_job_status(
            trade_date
        )

        return {
            "trade_date": trade_date,
            "summary": summary,
            "suggestions": suggestions,
            "job_status": job_status,
        }