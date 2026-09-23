"""Build raw, validation-ready evidence for the future Replay Coach."""
from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal
from math import isfinite
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


class ReplayCoachContextValidationError(ValueError):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class ReplayCoachContextService:
    """Transforms an assembled Replay response without fetching or mutating it."""

    CONTEXT_VERSION = "replay_coach_v2"
    INTERVAL_MINUTES = 5

    @classmethod
    def build_context(cls, replay_data: Dict[str, Any], trade_date: Optional[str] = None) -> Dict[str, Any]:
        data = deepcopy(replay_data)
        trade = data.get("executed_trade")
        if not isinstance(trade, dict):
            raise ReplayCoachContextValidationError(["No executed trade is available for Coach analysis."])

        errors: List[str] = []
        for field in ("trade_id", "symbol", "side", "entry_price", "entry_timestamp"):
            if trade.get(field) is None or trade.get(field) == "":
                errors.append(f"Executed trade is missing required field: {field}.")
        entry_time = cls._parse_timestamp(trade.get("entry_timestamp"), "entry timestamp", errors)
        exit_time = cls._parse_timestamp(trade.get("exit_timestamp"), "exit timestamp", errors) if trade.get("exit_timestamp") else None
        if entry_time and exit_time and exit_time < entry_time:
            errors.append("Exit timestamp occurs before entry timestamp.")

        selected_date = cls._parse_trade_date(trade_date, entry_time, errors)
        stock, stock_report = cls._prepare_candles(data.get("stock_candles"), "stock", selected_date)
        market, market_report = cls._prepare_candles(data.get("nifty_candles"), "market", selected_date)
        errors.extend(stock_report["errors"])
        errors.extend(market_report["errors"])
        if entry_time and entry_time.date() != selected_date:
            errors.append("Entry timestamp does not belong to the requested trade date.")
        if entry_time and not cls._within_session(entry_time, stock):
            errors.append("Entry timestamp falls outside the available stock candle session.")
        if exit_time and not cls._within_session(exit_time, stock):
            errors.append("Exit timestamp falls outside the available stock candle session.")
        if errors:
            raise ReplayCoachContextValidationError(errors)

        entry_candle = cls._candle_boundary(entry_time, stock)
        exit_candle = cls._candle_boundary(exit_time, stock) if exit_time else None
        warnings = stock_report["warnings"] + market_report["warnings"]
        if entry_candle is None:
            warnings.append("No stock candle matches the mapped entry timestamp.")
        if exit_time and exit_candle is None:
            warnings.append("No stock candle matches the mapped exit timestamp.")
        stock_times, market_times = set(stock_report["times"]), set(market_report["times"])
        if stock_times != market_times:
            warnings.append("Stock and market candle timestamps are not synchronized.")

        executed_trade = {
            key: cls._json_value(trade.get(key)) for key in (
                "trade_plan_id", "trade_id", "symbol", "side", "entry_price", "exit_price", "quantity",
                "pnl_amount", "pnl_pct", "trade_result", "exit_reason", "status", "order_id", "execution_source"
            )
        }
        executed_trade.update({
            "entry_timestamp": cls._iso(entry_time), "entry_candle_time": cls._iso(entry_candle),
            "exit_timestamp": cls._iso(exit_time), "exit_candle_time": cls._iso(exit_candle),
        })
        trade_data = cls._documented_trade_data(data.get("trade_data"))
        return {
            "context_version": cls.CONTEXT_VERSION, "trade_date": selected_date.isoformat(),
            "timezone": "Asia/Kolkata", "candle_interval_minutes": cls.INTERVAL_MINUTES,
            "executed_trade": executed_trade,
            # Keep the original documented plan alongside its deterministic,
            # Coach-only summary.  The public Replay response is untouched.
            "trade_data": trade_data,
            "documented_plan": cls._documented_plan(trade_data),
            "stock": {"symbol": str(trade["symbol"]).upper().removeprefix("NSE:"), "candle_count": len(stock), "candles": stock},
            "market": {"symbol": "NIFTY_FUTURES", "candle_count": len(market), "candles": market},
            "data_quality": {
                "stock_session_complete": not stock_report["missing"], "market_session_complete": not market_report["missing"],
                "timestamps_synchronized": stock_times == market_times,
                "entry_candle_found": entry_candle is not None, "exit_candle_found": exit_time is None or exit_candle is not None,
                "stock_volume_available": stock_report["volume_available"], "stock_vwap_available": stock_report["vwap_available"],
                "market_volume_available": market_report["volume_available"], "market_vwap_available": market_report["vwap_available"],
                "stock_missing_timestamps": [cls._iso(value) for value in stock_report["missing"]],
                "market_missing_timestamps": [cls._iso(value) for value in market_report["missing"]], "warnings": warnings,
            },
        }

    @classmethod
    def _documented_trade_data(cls, value: Any) -> Dict[str, Any]:
        """Return only the existing plan fields relevant to execution review."""
        value = value if isinstance(value, dict) else {}
        return {
            key: cls._json_value(value.get(key))
            for key in ("planned_entry_price", "planned_stop_price", "planned_target_price", "position_type", "plan_status")
        }

    @classmethod
    def _documented_plan(cls, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        entry = cls._finite_number(trade_data.get("planned_entry_price"))
        stop = cls._finite_number(trade_data.get("planned_stop_price"))
        target = cls._finite_number(trade_data.get("planned_target_price"))
        position_type = trade_data.get("position_type")
        position_type = str(position_type).upper() if position_type is not None else None
        risk = reward = ratio = None
        if entry is not None and stop is not None:
            risk = entry - stop if position_type == "LONG" else stop - entry if position_type == "SHORT" else None
        if entry is not None and target is not None:
            reward = target - entry if position_type == "LONG" else entry - target if position_type == "SHORT" else None
        risk = round(risk, 4) if risk is not None else None
        reward = round(reward, 4) if reward is not None else None
        if risk is not None and reward is not None and risk > 0:
            ratio = round(reward / risk, 4)
        return {
            "entry_price": entry, "stop_price": stop, "target_price": target,
            "position_type": position_type, "risk": risk, "reward": reward,
            "risk_reward_ratio": ratio, "stop_present": stop is not None,
        }

    @classmethod
    def _prepare_candles(cls, values: Any, source: str, requested_date: date):
        errors, warnings = [], []
        result, times = [], []
        if not isinstance(values, list):
            return result, {"errors": [f"{source.title()} candles are not a list."], "warnings": [], "times": [], "missing": [], "volume_available": False, "vwap_available": False}
        parsed = []
        for index, candle in enumerate(values):
            if not isinstance(candle, dict):
                errors.append(f"{source.title()} candle {index} is not an object."); continue
            timestamp = cls._parse_timestamp(candle.get("time"), f"{source} candle {index} timestamp", errors)
            if not timestamp: continue
            if timestamp.date() != requested_date: errors.append(f"{source.title()} candle {index} is outside the requested trade date.")
            parsed.append((timestamp, candle, index))
        original_times = [value[0] for value in parsed]
        if original_times != sorted(original_times): warnings.append(f"{source.title()} candles were sorted chronologically in the Coach context.")
        parsed.sort(key=lambda item: item[0])
        duplicates = {value for value in (item[0] for item in parsed) if sum(item[0] == value for item in parsed) > 1}
        if duplicates: errors.append(f"{source.title()} candles contain duplicate timestamps: {', '.join(cls._iso(item) for item in sorted(duplicates))}.")
        raw_volume = [item[1].get("volume") for item in parsed]
        raw_vwap = [item[1].get("vwap") for item in parsed]
        # Volume is independently available whenever at least one candle contains a real
        # numeric value.  Do not let unavailable VWAP or null values on other candles
        # discard genuine source volume.
        volume_available = any(cls._is_valid_volume(value) for value in raw_volume)
        vwap_available = bool(parsed) and any(value not in (None, 0, 0.0) for value in raw_vwap)
        if not volume_available: warnings.append(f"{source.title()} volume is unavailable.")
        if not vwap_available: warnings.append(f"{source.title()} VWAP is unavailable.")
        for timestamp, candle, index in parsed:
            try: o, h, l, c = (float(candle[key]) for key in ("open", "high", "low", "close"))
            except (KeyError, TypeError, ValueError): errors.append(f"{source.title()} candle {index} has invalid OHLC values."); continue
            if not (l <= o <= h and l <= c <= h and l <= h): errors.append(f"{source.title()} candle {index} has invalid OHLC range.")
            result.append({"time": cls._iso(timestamp), "open": cls._json_value(candle.get("open")), "high": cls._json_value(candle.get("high")), "low": cls._json_value(candle.get("low")), "close": cls._json_value(candle.get("close")), "volume": cls._json_value(candle.get("volume")), "vwap": cls._json_value(candle.get("vwap")) if vwap_available else None})
            times.append(timestamp)
        missing = cls._missing_times(times)
        return result, {"errors": errors, "warnings": warnings, "times": times, "missing": missing, "volume_available": volume_available, "vwap_available": vwap_available}

    @staticmethod
    def _missing_times(times):
        if len(times) < 2: return []
        missing, current, final = [], min(times), max(times)
        while current < final:
            current += timedelta(minutes=5)
            if current < final and current not in times: missing.append(current)
        return missing

    @classmethod
    def _candle_boundary(cls, timestamp, candles):
        if timestamp is None: return None
        boundary = timestamp.replace(minute=(timestamp.minute // 5) * 5, second=0, microsecond=0)
        return boundary if any(candle["time"] == cls._iso(boundary) for candle in candles) else None

    @staticmethod
    def _within_session(timestamp, candles):
        if not candles: return False
        times = [datetime.fromisoformat(candle["time"]) for candle in candles]
        return min(times) <= timestamp <= max(times) + timedelta(minutes=5)

    @staticmethod
    def _parse_trade_date(value, entry_time, errors):
        try: return date.fromisoformat(value) if value else entry_time.date()
        except (TypeError, ValueError): errors.append("Requested trade date is invalid."); return date.min

    @staticmethod
    def _parse_timestamp(value, label, errors):
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed.astimezone(IST) if parsed.tzinfo else parsed.replace(tzinfo=IST)
        except (TypeError, ValueError): errors.append(f"Invalid {label}."); return None

    @staticmethod
    def _iso(value): return value.isoformat(timespec="seconds") if value else None

    @staticmethod
    def _json_value(value): return float(value) if isinstance(value, Decimal) else value

    @staticmethod
    def _is_valid_volume(value):
        if isinstance(value, bool) or value is None:
            return False
        try:
            return isfinite(float(value))
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _finite_number(value):
        if isinstance(value, bool) or value is None:
            return None
        try:
            number = float(value)
            return number if isfinite(number) else None
        except (TypeError, ValueError):
            return None
