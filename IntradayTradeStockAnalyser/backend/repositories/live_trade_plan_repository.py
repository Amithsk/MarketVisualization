"""Persistence for the live-analysis trade-plan form.

This is deliberately separate from TradeJournal's ``trade_plan`` table.  That
table represents journal plans/trades and cannot hold the live form's editable
fields or lifecycle.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


class LiveTradePlanRepository:
    @staticmethod
    def ensure_schema(db: Session) -> None:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS live_trade_plan (
                id CHAR(36) PRIMARY KEY,
                account_scope VARCHAR(128) NOT NULL,
                symbol VARCHAR(64) NOT NULL,
                plan_date DATE NOT NULL,
                decision_time VARCHAR(64) NOT NULL,
                direction VARCHAR(8) NOT NULL,
                strategy VARCHAR(64) NOT NULL,
                entry_value VARCHAR(64) NOT NULL,
                stop_loss VARCHAR(64) NOT NULL,
                target1 VARCHAR(64) NOT NULL,
                target2 VARCHAR(64) NOT NULL,
                position_size VARCHAR(64) NOT NULL,
                reason_text TEXT NOT NULL,
                invalidation TEXT NOT NULL,
                entry_confirmation TEXT NOT NULL,
                status VARCHAR(16) NOT NULL,
                cancelled_at VARCHAR(64) NULL,
                cancellation_reason TEXT NULL,
                executed_at VARCHAR(64) NULL,
                exited_at VARCHAR(64) NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX live_trade_plan_lookup (account_scope, symbol, plan_date)
            )
        """))

    @staticmethod
    def list_for_symbol(db: Session, account_scope: str, symbol: str):
        rows = db.execute(text("""
            SELECT id, symbol, decision_time, direction, strategy, entry_value,
                   stop_loss, target1, target2, position_size, reason_text,
                   invalidation, entry_confirmation, status, cancelled_at,
                   cancellation_reason, executed_at, exited_at, plan_date,
                   updated_at
            FROM live_trade_plan
            WHERE account_scope = :account_scope AND symbol = :symbol
            ORDER BY decision_time DESC, created_at DESC
        """), {"account_scope": account_scope, "symbol": symbol}).mappings().all()
        return [dict(row) for row in rows]

    @staticmethod
    def active_for_symbol(db: Session, account_scope: str, symbol: str):
        return db.execute(text("""
            SELECT id FROM live_trade_plan
            WHERE account_scope = :account_scope AND symbol = :symbol
              AND status IN ('ACTIVE', 'EXECUTED')
            LIMIT 1 FOR UPDATE
        """), {"account_scope": account_scope, "symbol": symbol}).first()

    @staticmethod
    def create(db: Session, values: dict) -> None:
        db.execute(text("""
            INSERT INTO live_trade_plan (
                id, account_scope, symbol, plan_date, decision_time, direction,
                strategy, entry_value, stop_loss, target1, target2, position_size,
                reason_text, invalidation, entry_confirmation, status
            ) VALUES (
                :id, :account_scope, :symbol, :plan_date, :decision_time, :direction,
                :strategy, :entry, :stopLoss, :target1, :target2, :positionSize,
                :why, :invalidation, :entryConfirmation, 'ACTIVE'
            )
        """), values)

    @staticmethod
    def update(db: Session, account_scope: str, plan_id: str, values: dict) -> bool:
        result = db.execute(text("""
            UPDATE live_trade_plan SET direction=:direction, strategy=:strategy,
                entry_value=:entry, stop_loss=:stopLoss, target1=:target1,
                target2=:target2, position_size=:positionSize, reason_text=:why,
                invalidation=:invalidation, entry_confirmation=:entryConfirmation
            WHERE id=:id AND account_scope=:account_scope
        """), {**values, "id": plan_id, "account_scope": account_scope})
        return result.rowcount == 1

    @staticmethod
    def transition(db: Session, account_scope: str, plan_id: str, expected: str, next_status: str, action_time: str, reason: str | None) -> bool:
        fields = {"status": next_status}
        if next_status == "CANCELLED":
            fields.update(cancelled_at=action_time, cancellation_reason=reason)
        elif next_status == "EXECUTED":
            fields["executed_at"] = action_time
        elif next_status == "EXITED":
            fields["exited_at"] = action_time
        assignments = ", ".join(f"{key}=:{key}" for key in fields)
        result = db.execute(text(f"""
            UPDATE live_trade_plan SET {assignments}
            WHERE id=:id AND account_scope=:account_scope AND status=:expected
        """), {**fields, "id": plan_id, "account_scope": account_scope, "expected": expected})
        return result.rowcount == 1
