"""Deterministic, completed-candle evidence for an editable live trade-plan draft."""
from datetime import datetime, timedelta
from typing import Any

from backend.services.market_context_engine import calculate_market_context
from backend.services.event_detection.relative_strength_detector import calculate_percentage_move


class TradePlanDraftError(ValueError):
    pass


class TradePlanDraftService:
    @staticmethod
    def build(request: dict[str, Any]) -> dict[str, str]:
        direction = str(request.get("direction") or "").upper()
        if direction not in {"LONG", "SHORT"}:
            raise TradePlanDraftError("direction must be LONG or SHORT")

        strategy = str(request.get("strategy") or "").strip()
        decision_time = TradePlanDraftService._time(request.get("context_timestamp"))
        stock = TradePlanDraftService._completed(request.get("stock_candles"), decision_time)
        nifty = TradePlanDraftService._completed(request.get("nifty_candles"), decision_time)
        stock_context = calculate_market_context(stock, "STOCK")
        nifty_context = calculate_market_context(nifty, "NIFTY")

        nifty_observation = TradePlanDraftService._nifty_observation(nifty, nifty_context)
        stock_observation = TradePlanDraftService._stock_observation(stock, stock_context)
        relative_observation = TradePlanDraftService._relative_observation(stock, nifty)
        volume_observation = TradePlanDraftService._volume_observation(stock)
        setup = TradePlanDraftService._setup_phrase(direction, strategy)

        entry = TradePlanDraftService._level(request.get("entry"), "[entry level]")
        stop = TradePlanDraftService._level(request.get("stop_loss"), "[stop level]")
        target = TradePlanDraftService._level(request.get("target"), "[target level]")
        confirmation = TradePlanDraftService._text_or_placeholder(
            request.get("entry_confirmation"), "[entry confirmation]"
        )
        invalidation = TradePlanDraftService._text_or_placeholder(
            request.get("invalidation"), "[invalidation condition]"
        )

        description = (
            f"I'm considering a {'BUY' if direction == 'LONG' else 'SELL'} using {strategy or 'this setup'}: {setup}. "
            f"NIFTY is {nifty_observation}, while the stock is {stock_observation}{relative_observation}; "
            f"volume is {volume_observation}. "
            f"I will enter only after {confirmation}, with a stop at {stop} and a target at {target} [target reason]; "
            f"the setup fails if {invalidation}."
        )
        return {"draft": description, "context_timestamp": decision_time.isoformat(timespec="seconds")}

    @staticmethod
    def _time(value: Any) -> datetime:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError) as error:
            raise TradePlanDraftError("context_timestamp must be a valid timestamp") from error
        return parsed.replace(tzinfo=None)

    @classmethod
    def _completed(cls, candles: Any, context_start: datetime) -> list[dict[str, Any]]:
        if not isinstance(candles, list):
            return []
        result = []
        for candle in candles:
            if not isinstance(candle, dict):
                continue
            try:
                start = cls._time(candle.get("time"))
                normalized = {
                    "time": start.isoformat(sep=" ", timespec="seconds"),
                    "open": float(candle["open"]), "high": float(candle["high"]),
                    "low": float(candle["low"]), "close": float(candle["close"]),
                    "volume": float(candle["volume"]),
                }
            except (KeyError, TypeError, ValueError):
                continue
            # The selected timestamp is a candle start. Include it only when its
            # five-minute interval has completed; never consume later candles.
            if start + timedelta(minutes=5) <= context_start + timedelta(minutes=5):
                result.append(normalized)
        result.sort(key=lambda candle: candle["time"])
        return result

    @staticmethod
    def _nifty_observation(candles, context) -> str:
        if len(candles) < 2:
            return "[NIFTY condition unavailable]"
        move = calculate_percentage_move(candles[0]["open"], candles[-1]["close"])
        position = (context.get("vwap") or {}).get("position")
        direction = "up" if move > 0 else "down" if move < 0 else "flat"
        return f"moving {direction} from the session open" + (f" and {position.lower()} VWAP" if position else "")

    @staticmethod
    def _stock_observation(candles, context) -> str:
        if not candles:
            return "[stock VWAP/structure observation unavailable]"
        vwap = context.get("vwap") or {}
        position = vwap.get("position")
        resistance = context.get("nearest_active_resistance")
        support = context.get("nearest_active_support")
        structure = "near an active resistance zone" if resistance else "near an active support zone" if support else "without an active S/R zone confirmed"
        return f"{position.lower()} VWAP and {structure}" if position else f"{structure}; VWAP is unavailable"

    @staticmethod
    def _relative_observation(stock, nifty) -> str:
        stock_by_time = {c["time"]: c for c in stock}
        nifty_by_time = {c["time"]: c for c in nifty}
        common = sorted(set(stock_by_time) & set(nifty_by_time))
        if not common:
            return "; relative strength is unavailable because completed timestamps do not align"
        time = common[-1]
        stock_move = calculate_percentage_move(stock_by_time[time]["open"], stock_by_time[time]["close"])
        nifty_move = calculate_percentage_move(nifty_by_time[time]["open"], nifty_by_time[time]["close"])
        difference = stock_move - nifty_move
        if difference >= 1.0:
            return "; the stock is outperforming NIFTY in the matched completed candle"
        if difference <= -1.0:
            return "; the stock is underperforming NIFTY in the matched completed candle"
        return "; relative strength versus NIFTY is not established"

    @staticmethod
    def _volume_observation(candles) -> str:
        if len(candles) <= 5:
            return "[volume observation unavailable]"
        average = sum(c["volume"] for c in candles[-6:-1]) / 5
        if average <= 0:
            return "[volume observation unavailable]"
        ratio = candles[-1]["volume"] / average
        if ratio >= 1.5:
            return "expanded versus the prior five-candle average"
        return "not expanded versus the prior five-candle average"

    @staticmethod
    def _setup_phrase(direction: str, strategy: str) -> str:
        phrases = {
            ("LONG", "ORB Breakout"): "I'm looking for upward continuation through the opening-range high",
            ("SHORT", "ORB Breakout"): "I'm looking for downward continuation through the opening-range low",
            ("LONG", "ORB Breakdown"): "I will treat the opening-range breakdown as conflicting evidence and wait for a bullish reclaim",
            ("SHORT", "ORB Breakdown"): "I'm looking for downward continuation through the opening-range low",
            ("LONG", "VWAP Bounce"): "I'm looking for a bullish hold or reclaim of VWAP",
            ("SHORT", "VWAP Bounce"): "I'm looking for a failed VWAP bounce and renewed selling",
            ("LONG", "VWAP Rejection"): "I will treat VWAP rejection as conflicting evidence and wait for a bullish reclaim",
            ("SHORT", "VWAP Rejection"): "I'm looking for sellers to reject price at VWAP",
            ("LONG", "Pullback"): "I'm looking for a controlled pullback followed by bullish continuation",
            ("SHORT", "Pullback"): "I'm looking for a controlled pullback followed by bearish continuation",
            ("LONG", "Support / Resistance"): "I'm considering a possible reversal or continuation from support",
            ("SHORT", "Support / Resistance"): "I'm considering a possible reversal or continuation from resistance",
        }
        return phrases.get((direction, strategy), "I am waiting for the selected setup to become clear")

    @staticmethod
    def _level(value: Any, placeholder: str) -> str:
        try:
            return str(value) if value is not None and str(value).strip() else placeholder
        except Exception:
            return placeholder

    @staticmethod
    def _text_or_placeholder(value: Any, placeholder: str) -> str:
        text = str(value or "").strip()
        return text or placeholder
