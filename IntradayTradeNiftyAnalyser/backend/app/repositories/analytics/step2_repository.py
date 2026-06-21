#IntradayTradeNiftyAnalyser/backend/app/repositories/analytics/step1_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import text


class Step2Repository:
    """
    Repository responsible for STEP 2 validation data.

    READ ONLY.

    Sources:
        intradaytrading.step2_market_behavior
        intradaytrading.step2_market_open_behavior
        ml.ml_nifty_insights
    """

    def __init__(self, db: Session):
        self.db = db

    def get_market_behavior(self, trade_date: str):
        """
        STEP 2 market behavior snapshot.
        """

        query = text("""
            SELECT
                trade_date,
                index_open_behavior,
                early_volatility,
                market_participation,
                trade_allowed,
                frozen_at,
                created_at,
                updated_at
            FROM intradaytrading.step2_market_behavior
            WHERE trade_date = :trade_date
        """)

        result = self.db.execute(
            query,
            {"trade_date": trade_date}
        )

        return result.mappings().first()

    def get_market_open_behavior(self, trade_date: str):
        """
        STEP 2 decision output.
        """

        query = text("""
            SELECT
                trade_date,
                ir_high,
                ir_low,
                ir_range,
                ir_ratio,
                volatility_state,
                vwap_cross_count,
                vwap_state,
                range_hold_status,
                trade_permission,
                reason,
                decision_locked_at,
                created_at
            FROM intradaytrading.step2_market_open_behavior
            WHERE trade_date = :trade_date
        """)

        result = self.db.execute(
            query,
            {"trade_date": trade_date}
        )

        return result.mappings().first()

    def get_vwap_validation(self, trade_date: str):
        """
        Post-market NIFTY validation generated
        by the Analytical Engine.
        """

        query = text("""
            SELECT
                trade_date,
                trend_strength,
                vwap_cross_count,
                vwap_hold_percentage,
                analysis_status,
                rule_config_version,
                created_at
            FROM ml.ml_nifty_insights
            WHERE trade_date = :trade_date
        """)

        result = self.db.execute(
            query,
            {"trade_date": trade_date}
        )

        return result.mappings().first()