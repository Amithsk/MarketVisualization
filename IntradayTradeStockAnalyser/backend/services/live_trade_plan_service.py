from uuid import uuid4
from sqlalchemy.orm import Session
from backend.repositories.live_trade_plan_repository import LiveTradePlanRepository


class LiveTradePlanService:
    ACCOUNT_SCOPE = "anonymous"

    @staticmethod
    def _plan(row: dict) -> dict:
        return {
            "id": row["id"], "symbol": row["symbol"], "decisionTime": row["decision_time"],
            "direction": row["direction"], "strategy": row["strategy"],
            "entry": row["entry_value"], "stopLoss": row["stop_loss"], "target1": row["target1"],
            "target2": row["target2"], "positionSize": row["position_size"], "why": row["reason_text"],
            "invalidation": row["invalidation"], "entryConfirmation": row["entry_confirmation"],
            "status": row["status"], "cancelledAt": row["cancelled_at"],
            "cancellationReason": row["cancellation_reason"], "executedAt": row["executed_at"],
            "exitedAt": row["exited_at"], "planDate": str(row["plan_date"]),
        }

    @classmethod
    def list(cls, db: Session, symbol: str) -> list[dict]:
        LiveTradePlanRepository.ensure_schema(db)
        db.commit()
        return [cls._plan(row) for row in LiveTradePlanRepository.list_for_symbol(db, cls.ACCOUNT_SCOPE, symbol)]

    @classmethod
    def create(cls, db: Session, payload: dict) -> dict:
        LiveTradePlanRepository.ensure_schema(db)
        if LiveTradePlanRepository.active_for_symbol(db, cls.ACCOUNT_SCOPE, payload["symbol"]):
            db.rollback()
            raise ValueError("Resolve the current active/executed plan before creating another one.")
        # The public API uses camelCase, while the hand-written INSERT uses
        # snake_case names for these database columns.
        values = {
            **payload,
            "id": str(uuid4()),
            "account_scope": cls.ACCOUNT_SCOPE,
            "plan_date": payload["planDate"],
            "decision_time": payload["decisionTime"],
        }
        LiveTradePlanRepository.create(db, values)
        db.commit()
        return next(plan for plan in cls.list(db, payload["symbol"]) if plan["id"] == values["id"])

    @classmethod
    def update(cls, db: Session, plan_id: str, payload: dict) -> None:
        LiveTradePlanRepository.ensure_schema(db)
        if not LiveTradePlanRepository.update(db, cls.ACCOUNT_SCOPE, plan_id, payload):
            db.rollback()
            raise LookupError("Trade plan not found")
        db.commit()

    @classmethod
    def transition(cls, db: Session, plan_id: str, expected: str, status: str, action_time: str, reason: str | None) -> None:
        LiveTradePlanRepository.ensure_schema(db)
        if not LiveTradePlanRepository.transition(db, cls.ACCOUNT_SCOPE, plan_id, expected, status, action_time, reason):
            db.rollback()
            raise ValueError("Trade plan status changed; refresh and try again.")
        db.commit()
