# backend/app/services/step2_service.py

from datetime import date, datetime
from sqlalchemy.orm import Session
import logging
import traceback

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.schemas.step2_schema import (
    Step2PreviewResponse,
    Step2FrozenResponse,
    Step2OpenBehaviorSnapshot,
)

logger = logging.getLogger(__name__)

# -------------------------------------------------
# Internal helpers
# -------------------------------------------------

def _evaluate_trade_permission(
    index_open_behavior: str,
    early_volatility: str,
    market_participation: str,
) -> bool:
    """
    Decide whether trading is permitted.
    Conservative, deterministic, backend-owned.
    """

    logger.info(
        "[STEP2][SERVICE][_evaluate_trade_permission] inputs=%s",
        {
            "index_open_behavior": index_open_behavior,
            "early_volatility": early_volatility,
            "market_participation": market_participation,
        },
    )

    index_open_behavior = index_open_behavior.upper()
    early_volatility = early_volatility.upper()
    market_participation = market_participation.upper()

    if (
        index_open_behavior in ("STRONG_UP", "STRONG_DOWN")
        and market_participation == "BROAD"
        and early_volatility in ("NORMAL", "EXPANDING")
    ):
        logger.info("[STEP2][SERVICE][_evaluate_trade_permission] result=True")
        return True

    if early_volatility == "CHAOTIC" or market_participation == "THIN":
        logger.info("[STEP2][SERVICE][_evaluate_trade_permission] result=False (risk)")
        return False

    logger.info("[STEP2][SERVICE][_evaluate_trade_permission] result=False (default)")
    return False


def _to_snapshot(ctx: Step2MarketBehavior) -> Step2OpenBehaviorSnapshot:
    """
    Convert ORM model → API snapshot
    """

    logger.info(
        "[STEP2][SERVICE][_to_snapshot] ctx=%s",
        {
            "trade_date": ctx.trade_date,
            "index_open_behavior": ctx.index_open_behavior,
            "early_volatility": ctx.early_volatility,
            "market_participation": ctx.market_participation,
            "trade_allowed": ctx.trade_allowed,
            "frozen_at": ctx.frozen_at,
        },
    )

    return Step2OpenBehaviorSnapshot(
        trade_date=ctx.trade_date,
        mode="AUTO",
        manual_input_required=False,
        index_open_behavior=ctx.index_open_behavior,
        early_volatility=ctx.early_volatility,
        market_participation=ctx.market_participation,
        trade_allowed=ctx.trade_allowed,
        frozen_at=ctx.frozen_at,
    )


# -------------------------------------------------
# Public service methods
# -------------------------------------------------

def preview_step2_behavior(
    db: Session,
    trade_date: date,
) -> Step2PreviewResponse:

    logger.info("[STEP2][SERVICE][PREVIEW][START] trade_date=%s", trade_date)

    try:
        # STEP-1 gate (row existence == frozen)
        step1 = (
            db.query(Step1MarketContext)
            .filter(Step1MarketContext.trade_date == trade_date)
            .first()
        )

        logger.info(
            "[STEP2][SERVICE][PREVIEW] step1_found=%s created_at=%s",
            bool(step1),
            getattr(step1, "created_at", None),
        )

        if not step1:
            raise ValueError("STEP-1 must be frozen before STEP-2")

        existing = (
            db.query(Step2MarketBehavior)
            .filter(Step2MarketBehavior.trade_date == trade_date)
            .first()
        )

        logger.info(
            "[STEP2][SERVICE][PREVIEW] existing_step2=%s frozen_at=%s",
            bool(existing),
            getattr(existing, "frozen_at", None),
        )

        # Already frozen → AUTO
        if existing and existing.frozen_at:
            logger.info("[STEP2][SERVICE][PREVIEW] returning frozen snapshot")

            return Step2PreviewResponse(
                snapshot=_to_snapshot(existing),
                can_freeze=False,
            )

        # Manual default → MANUAL
        logger.info("[STEP2][SERVICE][PREVIEW] returning MANUAL default snapshot")

        snapshot = Step2OpenBehaviorSnapshot(
            trade_date=trade_date,
            mode="MANUAL",
            manual_input_required=True,
            index_open_behavior="UNKNOWN",
            early_volatility="UNKNOWN",
            market_participation="UNKNOWN",
            trade_allowed=False,
            frozen_at=None,
        )

        return Step2PreviewResponse(
            snapshot=snapshot,
            can_freeze=True,
        )

    except Exception as e:
        logger.error(
            "[STEP2][SERVICE][PREVIEW][FATAL] trade_date=%s error=%s",
            trade_date,
            str(e),
        )
        traceback.print_exc()
        raise


def freeze_step2_behavior(
    db: Session,
    trade_date: date,
    index_open_behavior: str,
    early_volatility: str,
    market_participation: str,
    trade_allowed: bool | None = None,
) -> Step2FrozenResponse:

    logger.info(
        "[STEP2][SERVICE][FREEZE][START] trade_date=%s payload=%s",
        trade_date,
        {
            "index_open_behavior": index_open_behavior,
            "early_volatility": early_volatility,
            "market_participation": market_participation,
        },
    )

    try:
        # STEP-1 gate
        step1 = (
            db.query(Step1MarketContext)
            .filter(Step1MarketContext.trade_date == trade_date)
            .first()
        )

        logger.info(
            "[STEP2][SERVICE][FREEZE] step1_found=%s created_at=%s",
            bool(step1),
            getattr(step1, "created_at", None),
        )

        if not step1:
            raise ValueError("STEP-1 must be frozen before STEP-2")

        existing = (
            db.query(Step2MarketBehavior)
            .filter(Step2MarketBehavior.trade_date == trade_date)
            .first()
        )

        logger.info(
            "[STEP2][SERVICE][FREEZE] existing_step2=%s frozen_at=%s",
            bool(existing),
            getattr(existing, "frozen_at", None),
        )

        if existing and existing.frozen_at:
            raise ValueError("STEP-2 is already frozen")

        index_open_behavior = index_open_behavior.strip().upper()
        early_volatility = early_volatility.strip().upper()
        market_participation = market_participation.strip().upper()

        computed_trade_allowed = _evaluate_trade_permission(
            index_open_behavior=index_open_behavior,
            early_volatility=early_volatility,
            market_participation=market_participation,
        )

        logger.info(
            "[STEP2][SERVICE][FREEZE] computed_trade_allowed=%s",
            computed_trade_allowed,
        )

        if existing:
            context = existing
            context.index_open_behavior = index_open_behavior
            context.early_volatility = early_volatility
            context.market_participation = market_participation
            context.trade_allowed = computed_trade_allowed
            context.frozen_at = datetime.utcnow()
        else:
            context = Step2MarketBehavior(
                trade_date=trade_date,
                index_open_behavior=index_open_behavior,
                early_volatility=early_volatility,
                market_participation=market_participation,
                trade_allowed=computed_trade_allowed,
                frozen_at=datetime.utcnow(),
            )
            db.add(context)

        db.commit()
        db.refresh(context)

        logger.info("[STEP2][SERVICE][FREEZE][SUCCESS] trade_date=%s", trade_date)

        return Step2FrozenResponse(
            snapshot=_to_snapshot(context),
        )

    except Exception as e:
        logger.error(
            "[STEP2][SERVICE][FREEZE][FATAL] trade_date=%s error=%s",
            trade_date,
            str(e),
        )
        traceback.print_exc()
        raise
