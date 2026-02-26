# =========================================================
# File: backend/app/services/step3_service.py
# =========================================================

from datetime import date, datetime
from sqlalchemy.orm import Session
import logging

from backend.app.models.step1_market_context import Step1MarketContext
from backend.app.models.step2_market_behavior import Step2MarketBehavior
from backend.app.models.step2_market_open_behavior import Step2MarketOpenBehavior
from backend.app.models.step3_execution_control import Step3ExecutionControl
from backend.app.models.step3_stock_selection import Step3StockSelection

from backend.app.schemas.step3_schema import (
    Step3ExecutionResponse,
    Step3ExecutionSnapshot,
    TradeCandidate,
    Step3ComputeResponse,
    Step3FreezeResponse,
    Step3StockContext,
)

# ✅ NEW — data provider (no business logic here)
from backend.app.services.nifty_stock_data_service import (
    get_universe_symbols,
    get_avg_traded_value_20d,
    get_atr_14_for_date,
    get_yesterday_candles,
)

logger = logging.getLogger(__name__)

LIQUIDITY_THRESHOLD_RUPEES = 1_000_000_000  # ₹100 Cr


# =========================================================
# STEP-3A — Deterministic Matrix
# =========================================================

def _derive_step3a(market_context: str | None, trade_permission: str | None):
    allowed: list[str] = []
    max_trades = 0

    if market_context == "TREND_DAY" and trade_permission == "YES":
        allowed = ["GAP_FOLLOW", "MOMENTUM"]
        max_trades = 3

    elif market_context == "TREND_DAY" and trade_permission == "LIMITED":
        allowed = ["MOMENTUM"]
        max_trades = 1

    elif market_context == "RANGE_UNCERTAIN_DAY" and trade_permission == "YES":
        allowed = ["MOMENTUM"]
        max_trades = 1

    elif market_context == "RANGE_UNCERTAIN_DAY" and trade_permission == "LIMITED":
        allowed = []
        max_trades = 0

    elif trade_permission == "NO":
        allowed = []
        max_trades = 0

    elif market_context == "NO_TRADE_DAY":
        allowed = []
        max_trades = 0

    execution_allowed = max_trades > 0
    return allowed, max_trades, execution_allowed


# =========================================================
# CORE DETERMINISTIC ENGINE (UNCHANGED)
# =========================================================

def _evaluate_stock(
    context: Step3StockContext,
    allowed_strategies: list[str],
) -> TradeCandidate:

    symbol = context.symbol.upper()

    if (
        context.avg_traded_value_20d < 100
        or not (1 <= context.atr_pct <= 4)
        or context.abnormal_candle
    ):
        return TradeCandidate(
            symbol=symbol,
            direction="LONG",
            strategy_used="NO_TRADE",
            reason="Rejected at Layer-1 (Tradability filter failed)",
            structure_valid=False,
        )

    stock_pct = (
        (context.stock_current_price - context.stock_open_0915)
        / context.stock_open_0915
        * 100
    )

    nifty_pct = (
        (context.nifty_current_price - context.nifty_open_0915)
        / context.nifty_open_0915
        * 100
    )

    rs = stock_pct - nifty_pct

    if rs >= 0.3:
        direction = "LONG"
    elif rs <= -0.3:
        direction = "SHORT"
    else:
        return TradeCandidate(
            symbol=symbol,
            direction="LONG",
            strategy_used="NO_TRADE",
            rs_value=rs,
            reason="Rejected at Layer-2 (RS Neutral)",
            structure_valid=False,
        )

    strategy = "NO_TRADE"

    if (
        "GAP_FOLLOW" in allowed_strategies
        and abs(context.gap_pct) >= 1.0
        and context.gap_hold
        and context.structure_valid
    ):
        strategy = "GAP_FOLLOW"

    elif (
        "MOMENTUM" in allowed_strategies
        and context.structure_valid
        and (
            (direction == "LONG" and context.price_vs_vwap == "ABOVE")
            or (direction == "SHORT" and context.price_vs_vwap == "BELOW")
        )
    ):
        strategy = "MOMENTUM"

    if strategy == "NO_TRADE":
        return TradeCandidate(
            symbol=symbol,
            direction=direction,
            strategy_used="NO_TRADE",
            rs_value=rs,
            reason="Rejected at Layer-3 (Strategy fit failed)",
            structure_valid=False,
        )

    intraday_high = context.stock_current_price
    intraday_low = context.stock_open_0915
    yesterday_close = context.stock_open_0915
    vwap_value = context.stock_current_price

    gap_high = None
    gap_low = None
    last_higher_low = None

    if strategy == "GAP_FOLLOW":
        gap_high = intraday_high
        gap_low = intraday_low
    elif strategy == "MOMENTUM":
        last_higher_low = intraday_low

    return TradeCandidate(
        symbol=symbol,
        direction=direction,
        strategy_used=strategy,
        rs_value=rs,
        gap_high=gap_high,
        gap_low=gap_low,
        intraday_high=intraday_high,
        intraday_low=intraday_low,
        last_higher_low=last_higher_low,
        yesterday_close=yesterday_close,
        vwap_value=vwap_value,
        structure_valid=context.structure_valid,
        reason="Qualified through deterministic Layer-1/2/3 evaluation",
    )


# =========================================================
# PREVIEW (UPDATED — LAYER1 INTEGRATED, CONTROL PERSISTENCE KEPT)
# =========================================================

def generate_step3_execution(db: Session, trade_date: date) -> Step3ExecutionResponse:

    decided_at = datetime.utcnow()

    step1 = db.query(Step1MarketContext).filter(
        Step1MarketContext.trade_date == trade_date
    ).first()

    step2_behavior = db.query(Step2MarketBehavior).filter(
        Step2MarketBehavior.trade_date == trade_date
    ).first()

    step2_open = db.query(Step2MarketOpenBehavior).filter(
        Step2MarketOpenBehavior.trade_date == trade_date
    ).first()

    if (
        not step1
        or not step2_behavior
        or not step2_behavior.frozen_at
        or not step2_open
    ):
        logger.info("[STEP3][STATE][PREVIEW_BLOCKED] trade_date=%s", trade_date)

        return Step3ExecutionResponse(
            snapshot=Step3ExecutionSnapshot(
                trade_date=trade_date,
                market_context=None,
                trade_permission=None,
                allowed_strategies=[],
                max_trades_allowed=0,
                execution_enabled=False,
                candidates_mode="MANUAL",
                candidates=[],
                generated_at=decided_at,
            ),
            can_freeze=False,
        )

    allowed_strategies, max_trades_allowed, execution_allowed = _derive_step3a(
        step1.final_market_context,
        step2_open.trade_permission,
    )

    logger.info(
        "[STEP3][STATE][STEP3A] trade_date=%s allowed=%s max_trades=%s execution=%s",
        trade_date,
        allowed_strategies,
        max_trades_allowed,
        execution_allowed,
    )

    # ==========================
    # CONTROL ROW PERSISTENCE
    # ==========================

    control_row = db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).first()

    if not control_row:
        control_row = Step3ExecutionControl(
            trade_date=trade_date,
            market_context=step1.final_market_context,
            trade_permission=step2_open.trade_permission,
            allowed_strategies=",".join(allowed_strategies),
            max_trades_allowed=max_trades_allowed,
            execution_allowed=int(execution_allowed),
            decided_at=decided_at,
        )
        db.add(control_row)
        db.commit()
    else:
        control_row.market_context = step1.final_market_context
        control_row.trade_permission = step2_open.trade_permission
        control_row.allowed_strategies = ",".join(allowed_strategies)
        control_row.max_trades_allowed = max_trades_allowed
        control_row.execution_allowed = int(execution_allowed)
        control_row.decided_at = decided_at
        db.commit()

    # ==========================
    # EARLY EXIT IF NO TRADE
    # ==========================

    if not execution_allowed:
        logger.info("[STEP3][STATE][NO_TRADE_EXIT] trade_date=%s", trade_date)

        return Step3ExecutionResponse(
            snapshot=Step3ExecutionSnapshot(
                trade_date=trade_date,
                market_context=step1.final_market_context,
                trade_permission=step2_open.trade_permission,
                allowed_strategies=allowed_strategies,
                max_trades_allowed=max_trades_allowed,
                execution_enabled=False,
                candidates_mode="MANUAL",
                candidates=[],
                generated_at=decided_at,
            ),
            can_freeze=False,
        )

    # ==========================
    # LAYER 1 — UNIVERSE
    # ==========================

    symbols = get_universe_symbols(db)
    logger.info("[STEP3][STATE][UNIVERSE_LOADED] trade_date=%s count=%s", trade_date, len(symbols))

    avg_map = get_avg_traded_value_20d(db, trade_date, symbols)
    atr_map = get_atr_14_for_date(db, trade_date, symbols)
    candle_map = get_yesterday_candles(db, trade_date, symbols)

    passed = []

    for symbol in symbols:

        avg_val = avg_map.get(symbol)
        atr = atr_map.get(symbol)
        candle = candle_map.get(symbol)

        if not avg_val or not atr or not candle:
            continue

        if avg_val < LIQUIDITY_THRESHOLD_RUPEES:
            continue

        atr_pct = (atr / candle["close"]) * 100 if candle["close"] else 0
        if atr_pct < 1 or atr_pct > 4:
            continue

        abnormal = (candle["high"] - candle["low"]) >= (2 * atr)
        if abnormal:
            continue

        passed.append({
            "symbol": symbol,
            "avg_traded_value_20d": avg_val,
            "atr_pct": round(atr_pct, 2),
            "abnormal_candle": abnormal,
        })

    logger.info("[STEP3][STATE][LAYER1_PASS] trade_date=%s passed=%s", trade_date, len(passed))

    passed.sort(key=lambda x: x["avg_traded_value_20d"], reverse=True)
    top6 = passed[:6]

    logger.info("[STEP3][STATE][TOP6_SELECTED] trade_date=%s count=%s", trade_date, len(top6))

    candidates = [
        TradeCandidate(
            symbol=c["symbol"],
            direction="LONG",
            strategy_used="NO_TRADE",
            avg_traded_value_20d=c["avg_traded_value_20d"],
            atr_pct=c["atr_pct"],
            abnormal_candle=c["abnormal_candle"],
            rs_value=None,
            gap_high=None,
            gap_low=None,
            intraday_high=None,
            intraday_low=None,
            last_higher_low=None,
            yesterday_close=None,
            vwap_value=None,
            structure_valid=False,
            reason="Layer-1 PASS (Manual Layer-2/3 pending)",
        )
        for c in top6
    ]

    logger.info("[STEP3][STATE][PREVIEW_SUCCESS] trade_date=%s", trade_date)

    return Step3ExecutionResponse(
        snapshot=Step3ExecutionSnapshot(
            trade_date=trade_date,
            market_context=step1.final_market_context,
            trade_permission=step2_open.trade_permission,
            allowed_strategies=allowed_strategies,
            max_trades_allowed=max_trades_allowed,
            execution_enabled=execution_allowed,
            candidates_mode="MANUAL",
            candidates=candidates,
            generated_at=decided_at,
        ),
        can_freeze=False,
    )


# =========================================================
# COMPUTE (UNCHANGED)
# =========================================================

def compute_step3_candidates(
    db: Session,
    trade_date: date,
    stocks: list[Step3StockContext],
) -> Step3ComputeResponse:

    preview = generate_step3_execution(db, trade_date)
    snapshot = preview.snapshot

    evaluated = []

    for context in stocks:
        candidate = _evaluate_stock(context, snapshot.allowed_strategies)
        evaluated.append(candidate)

    can_freeze = (
        snapshot.execution_enabled
        and any(c.strategy_used != "NO_TRADE" for c in evaluated)
    )

    logger.info(
        "[STEP3][STATE][COMPUTE] trade_date=%s candidates=%d can_freeze=%s",
        trade_date,
        len(evaluated),
        can_freeze,
    )

    return Step3ComputeResponse(
        snapshot=Step3ExecutionSnapshot(
            trade_date=trade_date,
            market_context=snapshot.market_context,
            trade_permission=snapshot.trade_permission,
            allowed_strategies=snapshot.allowed_strategies,
            max_trades_allowed=snapshot.max_trades_allowed,
            execution_enabled=snapshot.execution_enabled,
            candidates_mode="MANUAL",
            candidates=evaluated,
            generated_at=datetime.utcnow(),
        ),
        can_freeze=can_freeze,
    )


# =========================================================
# FREEZE (UNCHANGED)
# =========================================================

def freeze_step3_candidates(
    db: Session,
    trade_date: date,
    candidates: list[TradeCandidate],
) -> Step3FreezeResponse:

    decided_at = datetime.utcnow()

    control_row = db.query(Step3ExecutionControl).filter(
        Step3ExecutionControl.trade_date == trade_date
    ).first()

    if not control_row:
        raise ValueError("Preview must be generated before freeze.")

    qualified = [c for c in candidates if c.strategy_used != "NO_TRADE"]

    if not qualified:
        raise ValueError("No qualified trades available to freeze.")

    qualified = qualified[:control_row.max_trades_allowed]

    db.query(Step3StockSelection).filter(
        Step3StockSelection.trade_date == trade_date
    ).delete()

    for c in qualified:
        db.add(
            Step3StockSelection(
                trade_date=trade_date,
                symbol=c.symbol,
                direction=c.direction,
                strategy_used=c.strategy_used,
                rs_value=c.rs_value,
                gap_high=c.gap_high,
                gap_low=c.gap_low,
                intraday_high=c.intraday_high,
                intraday_low=c.intraday_low,
                last_higher_low=c.last_higher_low,
                yesterday_close=c.yesterday_close,
                vwap_value=c.vwap_value,
                structure_valid=int(c.structure_valid),
                reason=c.reason,
                evaluated_at=decided_at,
            )
        )

    db.commit()

    logger.info(
        "[STEP3][STATE][FREEZE_SUCCESS] trade_date=%s persisted=%d",
        trade_date,
        len(qualified),
    )

    return Step3FreezeResponse(
        snapshot=Step3ExecutionSnapshot(
            trade_date=trade_date,
            market_context=control_row.market_context,
            trade_permission=control_row.trade_permission,
            allowed_strategies=(
                control_row.allowed_strategies.split(",")
                if control_row.allowed_strategies
                else []
            ),
            max_trades_allowed=control_row.max_trades_allowed,
            execution_enabled=bool(control_row.execution_allowed),
            candidates_mode="AUTO",
            candidates=qualified,
            generated_at=decided_at,
        ),
        can_freeze=False,
    )