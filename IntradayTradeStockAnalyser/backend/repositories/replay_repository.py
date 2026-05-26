#IntradayTradeStockAnalyser/backend/repositories/replay_repository.py

from sqlalchemy import text
from sqlalchemy.orm import Session


class ReplayRepository:

    @staticmethod
    def get_trade_metadata(
        db: Session,
        trade_date: str,
        stock: str
    ):

        query = text("""

            SELECT
                strategy,
                position_type,
                trade_mode,
                setup_description,
                planned_entry_price,
                planned_stop_price,
                planned_target_price,
                plan_status

            FROM trade_plan

            WHERE plan_date = :trade_date

            AND symbol = :stock

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date,
                "stock": stock
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "strategy": row[0],

            "position_type": row[1],

            "trade_mode": row[2],

            "setup_description": row[3],

            "planned_entry_price": float(row[4]),

            "planned_stop_price": float(row[5]),

            "planned_target_price": float(row[6]),

            "plan_status": row[7]

        }

    @staticmethod
    def get_market_context(
        db: Session,
        trade_date: str
    ):

        query = text("""

            SELECT
                preopen_price,
                gap_pct,
                gap_class,
                prior_range_size,
                prior_day_overlap,
                prior_structure_state,
                final_market_context,
                final_reason

            FROM step1_market_context

            WHERE trade_date = :trade_date

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "preopen_price": (
                float(row[0])
                if row[0] is not None
                else None
            ),

            "gap_pct": (
                float(row[1])
                if row[1] is not None
                else None
            ),

            "gap_class": row[2],

            "prior_range_size": row[3],

            "prior_day_overlap": row[4],

            "prior_structure_state": row[5],

            "final_market_context": row[6],

            "final_reason": row[7]

        }

    @staticmethod
    def get_market_behavior(
        db: Session,
        trade_date: str
    ):

        query = text("""

            SELECT
                index_open_behavior,
                early_volatility,
                market_participation,
                trade_allowed

            FROM step2_market_behavior

            WHERE trade_date = :trade_date

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "index_open_behavior": row[0],

            "early_volatility": row[1],

            "market_participation": row[2],

            "trade_allowed": bool(row[3])

        }

    @staticmethod
    def get_market_open_behavior(
        db: Session,
        trade_date: str
    ):

        query = text("""

            SELECT
                ir_high,
                ir_low,
                ir_range,
                ir_ratio,
                volatility_state,
                vwap_cross_count,
                vwap_state,
                range_hold_status,
                trade_permission,
                reason

            FROM step2_market_open_behavior

            WHERE trade_date = :trade_date

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "ir_high": (
                float(row[0])
                if row[0] is not None
                else None
            ),

            "ir_low": (
                float(row[1])
                if row[1] is not None
                else None
            ),

            "ir_range": (
                float(row[2])
                if row[2] is not None
                else None
            ),

            "ir_ratio": (
                float(row[3])
                if row[3] is not None
                else None
            ),

            "volatility_state": row[4],

            "vwap_cross_count": row[5],

            "vwap_state": row[6],

            "range_hold_status": row[7],

            "trade_permission": row[8],

            "reason": row[9]

        }

    @staticmethod
    def get_execution_control(
        db: Session,
        trade_date: str
    ):

        query = text("""

            SELECT
                market_context,
                trade_permission,
                allowed_strategies,
                max_trades_allowed,
                execution_allowed

            FROM step3_execution_control

            WHERE trade_date = :trade_date

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "market_context": row[0],

            "trade_permission": row[1],

            "allowed_strategies": (
                row[2].split(",")
                if row[2]
                else []
            ),

            "max_trades_allowed": row[3],

            "execution_allowed": bool(row[4])

        }

    @staticmethod
    def get_stock_selection_context(
        db: Session,
        trade_date: str,
        stock: str
    ):

        query = text("""

            SELECT
                direction,
                strategy_used,
                rs_value,
                gap_high,
                gap_low,
                intraday_high,
                intraday_low,
                last_higher_low,
                yesterday_close,
                vwap_value,
                structure_valid,
                reason,
                tradable,
                rejection_tag

            FROM step3_stock_selection

            WHERE trade_date = :trade_date

            AND symbol = :stock

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date,
                "stock": stock
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "direction": row[0],

            "strategy_used": row[1],

            "rs_value": (
                float(row[2])
                if row[2] is not None
                else None
            ),

            "gap_high": (
                float(row[3])
                if row[3] is not None
                else None
            ),

            "gap_low": (
                float(row[4])
                if row[4] is not None
                else None
            ),

            "intraday_high": (
                float(row[5])
                if row[5] is not None
                else None
            ),

            "intraday_low": (
                float(row[6])
                if row[6] is not None
                else None
            ),

            "last_higher_low": (
                float(row[7])
                if row[7] is not None
                else None
            ),

            "yesterday_close": (
                float(row[8])
                if row[8] is not None
                else None
            ),

            "vwap_value": (
                float(row[9])
                if row[9] is not None
                else None
            ),

            "structure_valid": bool(row[10]),

            "reason": row[11],

            "tradable": bool(row[12]),

            "rejection_tag": row[13]

        }

    @staticmethod
    def get_trade_construction(
        db: Session,
        trade_date: str,
        stock: str
    ):

        query = text("""

            SELECT
                strategy_used,
                direction,
                structure_valid,
                entry_price,
                stop_loss,
                risk_per_share,
                quantity,
                target_price,
                trade_status,
                block_reason

            FROM step4_trade_construction

            WHERE trade_date = :trade_date

            AND symbol = :stock

            LIMIT 1

        """)

        result = db.execute(
            query,
            {
                "trade_date": trade_date,
                "stock": stock
            }
        )

        row = result.fetchone()

        if not row:
            return {}

        return {

            "strategy_used": row[0],

            "direction": row[1],

            "structure_valid": bool(row[2]),

            "entry_price": (
                float(row[3])
                if row[3] is not None
                else None
            ),

            "stop_loss": (
                float(row[4])
                if row[4] is not None
                else None
            ),

            "risk_per_share": (
                float(row[5])
                if row[5] is not None
                else None
            ),

            "quantity": row[6],

            "target_price": (
                float(row[7])
                if row[7] is not None
                else None
            ),

            "trade_status": row[8],

            "block_reason": row[9]

        }