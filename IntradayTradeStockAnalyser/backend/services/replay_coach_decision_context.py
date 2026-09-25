"""Deterministic, no-lookahead facts used by Replay Coach decisions."""
from datetime import datetime, timedelta
from statistics import median
from typing import Any


MINIMUM_REWARD_RISK_RATIO = 4.0


class ReplayCoachDecisionContext:
    @classmethod
    def build(cls, stock: list[dict], market: list[dict], entry_time: str, documented_plan: dict) -> dict:
        entry = datetime.fromisoformat(entry_time)
        completed_stock = cls._completed(stock, entry)
        completed_market = cls._completed(market, entry)
        last_stock = completed_stock[-1] if completed_stock else None
        last_market = completed_market[-1] if completed_market else None
        return {
            "decision_timing": {
                "entry_time": entry_time,
                "containing_candle_start": cls._containing_start(entry).isoformat(timespec="seconds"),
                "containing_candle_end": (cls._containing_start(entry) + timedelta(minutes=5)).isoformat(timespec="seconds"),
                "containing_candle_complete_at_entry": False,
                "last_completed_stock_candle_time": last_stock.get("time") if last_stock else None,
                "last_completed_market_candle_time": last_market.get("time") if last_market else None,
            },
            "stock_direction": cls._direction(completed_stock, with_vwap=True),
            "nifty_direction": cls._direction(completed_market, with_vwap=False),
            "relative_strength": cls._relative_strength(completed_stock, completed_market),
            "stock_relative_volume": cls._volume(completed_stock),
            "nifty_relative_volume": cls._volume(completed_market),
            "recent_volatility": cls._volatility(completed_stock, documented_plan),
            "support_resistance": cls._levels(completed_stock, documented_plan.get("entry_price")),
            "risk_economics": cls._economics(documented_plan),
        }

    @staticmethod
    def _containing_start(value: datetime) -> datetime:
        return value.replace(minute=(value.minute // 5) * 5, second=0, microsecond=0)

    @classmethod
    def _completed(cls, candles: list[dict], entry: datetime) -> list[dict]:
        # A candle is decision evidence only once its five-minute interval ended.
        return [c for c in candles if datetime.fromisoformat(c["time"]) + timedelta(minutes=5) <= entry]

    @classmethod
    def _direction(cls, values: list[dict], with_vwap: bool) -> dict:
        if not values:
            return {"classification": "UNAVAILABLE"}
        last = values[-1]; close = float(last["close"])
        def ret(n):
            return round((close - float(values[-n]["close"])) / float(values[-n]["close"]) * 100, 4) if len(values) >= n else None
        vwap = last.get("vwap") if with_vwap else None
        distance = round(close - float(vwap), 4) if vwap not in (None, 0) else None
        pct = round(distance / float(vwap) * 100, 4) if distance is not None else None
        r3, r5 = ret(3), ret(5)
        positive = (r3 is not None and r3 > 0) and (r5 is not None and r5 > 0) and (not with_vwap or distance is not None and distance > 0)
        negative = (r3 is not None and r3 < 0) and (r5 is not None and r5 < 0) and (not with_vwap or distance is not None and distance < 0)
        return {"last_completed_close": close, "vwap": vwap, "distance_from_vwap_points": distance, "distance_from_vwap_pct": pct, "three_candle_return_pct": r3, "five_candle_return_pct": r5, "classification": "BULLISH" if positive else "BEARISH" if negative else "NEUTRAL"}

    @staticmethod
    def _relative_strength(stock, market):
        n = min(len(stock), len(market), 5)
        if n < 2: return {"window_candles": n, "stock_return_pct": None, "nifty_return_pct": None, "relative_strength_pct": None}
        calc = lambda values: (float(values[-1]["close"]) - float(values[-n]["close"])) / float(values[-n]["close"]) * 100
        s, m = calc(stock), calc(market)
        return {"window_candles": n, "stock_return_pct": round(s, 4), "nifty_return_pct": round(m, 4), "relative_strength_pct": round(s-m, 4)}

    @staticmethod
    def _volume(values):
        if not values or values[-1].get("volume") is None: return {"last_completed_volume": None}
        prior = [float(c["volume"]) for c in values[:-1] if c.get("volume") is not None]
        result = {"last_completed_volume": float(values[-1]["volume"])}
        for n in (5, 10, 20):
            base = median(prior[-n:]) if len(prior) >= n else None
            result[f"previous_{n}_candle_median"] = base
            result[f"ratio_vs_{n}_candle_median"] = round(result["last_completed_volume"] / base, 4) if base else None
        return result

    @staticmethod
    def _volatility(values, plan):
        if not values: return {"last_completed_range": None}
        ranges = [float(c["high"]) - float(c["low"]) for c in values]
        result = {"last_completed_range": round(ranges[-1], 4)}
        for n in (5, 10): result[f"previous_{n}_candle_median_range"] = round(median(ranges[-(n+1):-1]), 4) if len(ranges) > n else None
        econ = ReplayCoachDecisionContext._economics(plan); base = result["previous_10_candle_median_range"] or result.get("previous_5_candle_median_range")
        result.update({"target_distance_multiple": round(econ["reward"] / base, 4) if base and econ["reward"] is not None else None, "stop_distance_multiple": round(econ["risk"] / base, 4) if base and econ["risk"] is not None else None})
        return result

    @staticmethod
    def _levels(values, entry):
        # Candidate levels require at least two clustered completed-candle extrema.
        if len(values) < 2 or entry is None: return []
        tolerance = round(float(entry) * 0.001, 4); levels = []
        for kind, key in (("SUPPORT", "low"), ("RESISTANCE", "high")):
            for candle in values:
                price = float(candle[key]); touches = [c for c in values if abs(float(c[key])-price) <= tolerance]
                if len(touches) >= 2:
                    levels.append({"level": round(sum(float(c[key]) for c in touches)/len(touches), 4), "level_type": kind, "touch_count": len(touches), "touch_timestamps": [c["time"] for c in touches], "clustering_tolerance": tolerance, "distance_from_proposed_entry": round(float(entry)-price, 4) if entry else None, "established_before_entry": True})
                    break
        return levels

    @staticmethod
    def _economics(plan):
        entry, stop, target, side = (plan.get(k) for k in ("entry_price", "stop_price", "target_price", "position_type"))
        if None in (entry, stop, target) or side not in ("LONG", "SHORT"): return {"required_ratio": MINIMUM_REWARD_RISK_RATIO}
        risk = float(entry)-float(stop) if side == "LONG" else float(stop)-float(entry)
        reward = float(target)-float(entry) if side == "LONG" else float(entry)-float(target)
        ratio = reward/risk if risk > 0 else None
        maximum_risk = reward/MINIMUM_REWARD_RISK_RATIO if reward > 0 else None
        allowable_stop = float(entry)-maximum_risk if side == "LONG" and maximum_risk is not None else float(entry)+maximum_risk if maximum_risk is not None else None
        return {"entry": entry, "stop": stop, "target": target, "risk": round(risk,4), "reward": round(reward,4), "reward_risk_ratio": round(ratio,4) if ratio is not None else None, "required_ratio": MINIMUM_REWARD_RISK_RATIO, "ratio_shortfall": round(max(0, MINIMUM_REWARD_RISK_RATIO-(ratio or 0)),4), "maximum_allowed_risk": round(maximum_risk,4) if maximum_risk is not None else None, "allowable_stop": round(allowable_stop,4) if allowable_stop is not None else None, "break_even_win_rate": round(risk/(risk+reward),4) if risk > 0 and reward > 0 else None, "equal_wins_to_recover_one_loss": round(risk/reward,4) if risk > 0 and reward > 0 else None, "take_valid": bool(ratio is not None and ratio >= MINIMUM_REWARD_RISK_RATIO)}
