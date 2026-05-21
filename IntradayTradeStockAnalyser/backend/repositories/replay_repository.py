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