#IntradayTradeNiftyAnalyser/backend/app/repositories/analytics/learning_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import text


class LearningRepository:
    """
    Repository responsible for fetching
    learning-related analytics data.

    READ ONLY.

    Sources:
        ml.ml_summary
        ml.ml_suggestions
        ml.ml_job_tracker
    """

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, trade_date: str):
        """
        Returns summary record for trade_date.
        """

        query = text("""
            SELECT
                trade_date,
                summary_text,
                analysis_status,
                rule_config_version,
                created_at
            FROM ml.ml_summary
            WHERE trade_date = :trade_date
        """)

        result = self.db.execute(
            query,
            {"trade_date": trade_date}
        )

        return result.mappings().first()

    def get_suggestions(self, trade_date: str):
        """
        Returns all suggestions for trade_date.
        """

        query = text("""
            SELECT
                trade_date,
                rule_name,
                current_value,
                suggested_value,
                support_metric,
                impact,
                confidence,
                priority,
                created_at
            FROM ml.ml_suggestions
            WHERE trade_date = :trade_date
            ORDER BY
                CASE priority
                    WHEN 'HIGH' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'LOW' THEN 3
                    ELSE 4
                END
        """)

        result = self.db.execute(
            query,
            {"trade_date": trade_date}
        )

        return result.mappings().all()

    def get_job_status(self, trade_date: str):
        """
        Returns latest job execution status
        for the specified trade date.
        """

        query = text("""
            SELECT
                execution_id,
                trade_date,
                status,
                start_time,
                end_time,
                last_updated_at
            FROM ml.ml_job_tracker
            WHERE trade_date = :trade_date
            ORDER BY last_updated_at DESC
            LIMIT 1
        """)

        result = self.db.execute(
            query,
            {"trade_date": trade_date}
        )

        return result.mappings().first()