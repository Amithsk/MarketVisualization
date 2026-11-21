"""Deterministic decision-time facts; no candle ending after entry is used."""
from datetime import datetime, timedelta
from statistics import median

MINIMUM_REWARD_RISK_RATIO = 4.0


class ReplayCoachDecisionContext:
    VWAP_NEAR_RANGE_FRACTION = .15
    VWAP_NEAR_MIN_PCT = .10
    STRUCTURE_INVALIDATION_CLOSES = 2

    @classmethod
    def build(cls, stock, market, entry_time, documented_plan):
        entry = datetime.fromisoformat(entry_time)
        s, n = cls._completed(stock, entry), cls._completed(market, entry)
        ss, ns = cls._structure(s), cls._structure(n)
        sm, nm = cls._momentum(s), cls._momentum(n)
        sv, nv = cls._vwap(s), cls._vwap(n)
        svol, nvol = cls._volume(s), cls._volume(n)
        composite = cls._composite(ss["classification"], sm["classification"])
        return {
            "decision_timing": {"entry_time": entry_time, "containing_candle_start": cls._start(entry).isoformat(timespec="seconds"), "containing_candle_end": (cls._start(entry)+timedelta(minutes=5)).isoformat(timespec="seconds"), "containing_candle_complete_at_entry": False, "last_completed_stock_candle_time": s[-1]["time"] if s else None, "last_completed_market_candle_time": n[-1]["time"] if n else None},
            "stock_session_structure": ss, "stock_recent_momentum": sm, "stock_latest_completed_candle": cls._latest_candle(s), "stock_vwap_location": sv, "stock_volume_context": cls._volume_context(svol),
            "nifty_session_structure": ns, "nifty_recent_momentum": nm, "nifty_vwap_location": nv, "nifty_volume_context": cls._volume_context(nvol),
            "stock_nifty_relationship": cls._relationship(ss["classification"], sm["classification"], ns["classification"], nm["classification"]),
            "decision_time_market_context": {"classification": composite, "stock_completed_candle_count": len(s), "nifty_completed_candle_count": len(n)},
            # Compatibility: this is composite context, not last-candle direction.
            "stock_direction": {**sv, **sm, "classification": composite, "session_structure": ss["classification"]},
            "nifty_direction": {**nv, **nm, "classification": ns["classification"], "session_structure": ns["classification"]},
            "relative_strength": cls._relative_strength(s, n), "stock_relative_volume": svol, "nifty_relative_volume": nvol,
            "recent_volatility": cls._volatility(s, documented_plan), "support_resistance": cls._levels(s, documented_plan.get("entry_price")), "risk_economics": cls._economics(documented_plan),
        }

    @staticmethod
    def _start(value): return value.replace(minute=(value.minute//5)*5, second=0, microsecond=0)
    @staticmethod
    def _completed(candles, entry): return [c for c in candles if datetime.fromisoformat(c["time"])+timedelta(minutes=5) <= entry]
    @staticmethod
    def _trend(values):
        if len(values) < 2: return "UNKNOWN"
        return "UP" if values[-1]["price"] > values[-2]["price"] else "DOWN" if values[-1]["price"] < values[-2]["price"] else "FLAT"
    @classmethod
    def _structure(cls, values):
        required = 2
        if len(values) < 3: return {"classification":"NOT_ASSESSABLE" if not values else "UNCONFIRMED","completed_candle_count":len(values),"required_swing_highs":required,"required_swing_lows":required,"confirmed_swing_highs":[],"confirmed_swing_lows":[],"swing_high_trend":"UNKNOWN","swing_low_trend":"UNKNOWN","explanation":"There are not enough completed candles to confirm swing points."}
        highs=[]; lows=[]
        for i in range(1,len(values)-1):
            a,b,c=values[i-1],values[i],values[i+1]
            if float(b["high"])>float(a["high"]) and float(b["high"])>float(c["high"]): highs.append({"time":b["time"],"price":float(b["high"])})
            if float(b["low"])<float(a["low"]) and float(b["low"])<float(c["low"]): lows.append({"time":b["time"],"price":float(b["low"])})
        ht,lt=cls._trend(highs),cls._trend(lows)
        enough=len(highs)>=required and len(lows)>=required
        direction="UNCONFIRMED" if not enough else "BULLISH" if ht==lt=="UP" else "BEARISH" if ht==lt=="DOWN" else "RANGE" if ht==lt=="FLAT" else "MIXED"
        return {"classification":direction,"completed_candle_count":len(values),"required_swing_highs":required,"required_swing_lows":required,"confirmed_swing_highs":highs,"confirmed_swing_lows":lows,"swing_high_trend":ht,"swing_low_trend":lt,"explanation":f"Only {len(highs)} swing highs and {len(lows)} swing lows are confirmed; {required} of each are required." if not enough else f"Confirmed swing-high trend is {ht.lower()} and swing-low trend is {lt.lower()}."}
    @staticmethod
    def _momentum(values):
        if not values:return {"classification":"NOT_ASSESSABLE","three_candle_return_pct":None,"five_candle_return_pct":None}
        close=float(values[-1]["close"])
        def window(count):
            if len(values)<count:return None
            start,end=values[-count],values[-1]; pct=round((close-float(start["close"]))/float(start["close"])*100,4)
            return {"start_time":start["time"],"start_close":float(start["close"]),"end_time":end["time"],"end_close":close,"return_pct":pct,"formula":f"({close:.2f} - {float(start['close']):.2f}) / {float(start['close']):.2f} × 100"}
        three,five=window(3),window(5); values_=[x["return_pct"] for x in (three,five) if x]; signs=[x>0 for x in values_]
        return {"classification":"BULLISH" if signs and all(signs) else "BEARISH" if signs and not any(signs) else "MIXED" if len(signs)==2 else "NEUTRAL","three_candle_return_pct":three["return_pct"] if three else None,"five_candle_return_pct":five["return_pct"] if five else None,"three_candle":three,"five_candle":five,"last_completed_close":close}

    @staticmethod
    def _latest_candle(values):
        if len(values)<2:return {"classification":"NOT_ASSESSABLE","explanation":"A previous completed candle is required for comparison."}
        c,p=values[-1],values[-2]; o,h,l,close=(float(c[k]) for k in ("open","high","low","close")); body=round(close-o,4)
        classification="INSIDE_RANGE" if h<=float(p["high"]) and l>=float(p["low"]) else "RECOVERY" if body>0 and l>=float(p["low"]) and h<float(p["high"]) else "BULLISH_PROGRESS" if body>0 and h>float(p["high"]) else "BEARISH_PROGRESS" if body<0 and l<float(p["low"]) else "PULLBACK" if body<0 else "PAUSE" if body==0 else "MIXED"
        return {"interval_start":c["time"],"previous_interval_start":p["time"],"open":o,"high":h,"low":l,"close":close,"body_change":body,"body_pct":round(body/o*100,4) if o else None,"previous_high":float(p["high"]),"previous_low":float(p["low"]),"classification":classification,"explanation":f"The candle {'closed above' if body>0 else 'closed below' if body<0 else 'matched'} its open and {'did not reclaim' if h<float(p['high']) else 'exceeded'} the previous high."}
    @classmethod
    def _vwap(cls, values):
        if not values:return {"location":"UNAVAILABLE","last_completed_close":None,"vwap":None,"distance_from_vwap_points":None,"distance_from_vwap_pct":None,"near_tolerance_points":None}
        last=values[-1]; close=float(last["close"]); raw=last.get("vwap")
        if raw in (None,0):return {"location":"UNAVAILABLE","last_completed_close":close,"vwap":None,"distance_from_vwap_points":None,"distance_from_vwap_pct":None,"near_tolerance_points":None}
        vwap=float(raw); distance=round(close-vwap,4); tolerance=round(max((float(last["high"])-float(last["low"]))*cls.VWAP_NEAR_RANGE_FRACTION,close*cls.VWAP_NEAR_MIN_PCT/100),4)
        return {"location":"NEAR" if abs(distance)<=tolerance else "ABOVE" if distance>0 else "BELOW","last_completed_close":close,"vwap":vwap,"distance_from_vwap_points":distance,"distance_from_vwap_pct":round(distance/vwap*100,4),"near_tolerance_points":tolerance}
    @staticmethod
    def _volume(values):
        if not values or values[-1].get("volume") is None:return {"last_completed_volume":None}
        prior=[float(c["volume"]) for c in values[:-1] if c.get("volume") is not None]; result={"last_completed_volume":float(values[-1]["volume"])}
        for n in (5,10,20):
            base=median(prior[-n:]) if len(prior)>=n else None; result[f"previous_{n}_candle_median"]=base; result[f"ratio_vs_{n}_candle_median"]=round(result["last_completed_volume"]/base,4) if base else None
        return result
    @staticmethod
    def _volume_context(volume):
        ratio=volume.get("ratio_vs_5_candle_median"); return {"classification":"UNAVAILABLE" if ratio is None else "STRONG" if ratio>=1.2 else "WEAK" if ratio<.8 else "NORMAL","ratio_vs_5_candle_median":ratio,"last_completed_volume":volume.get("last_completed_volume"),"previous_5_candle_median":volume.get("previous_5_candle_median")}
    @staticmethod
    def _composite(structure,momentum):
        if structure=="BULLISH":return "BULLISH_CONTINUATION" if momentum=="BULLISH" else "BULLISH_STRUCTURE_PULLBACK" if momentum=="BEARISH" else "MIXED"
        if structure=="BEARISH":return "BEARISH_CONTINUATION" if momentum=="BEARISH" else "BEARISH_STRUCTURE_BOUNCE" if momentum=="BULLISH" else "MIXED"
        return "INSUFFICIENT_DATA" if structure=="INSUFFICIENT_DATA" else "MIXED"
    @staticmethod
    def _relationship(ss,sm,ns,nm):
        if ns=="BULLISH" and ss=="BULLISH": code,meaning="NIFTY_BULLISH_STOCK_BULLISH","market alignment"
        elif ns=="BULLISH": code,meaning="NIFTY_BULLISH_STOCK_WEAK","relative weakness"
        elif ss=="BULLISH": code,meaning="NIFTY_WEAK_STOCK_BULLISH","relative strength or divergence"
        elif ns in ("BEARISH","MIXED","RANGE") and ss in ("BEARISH","MIXED","RANGE"): code,meaning="NIFTY_WEAK_STOCK_WEAK","market weakness alignment"
        else: code,meaning="MIXED_OR_UNCLEAR","unclear relationship"
        return {"classification":code,"meaning":meaning,"stock_session_structure":ss,"stock_recent_momentum":sm,"nifty_session_structure":ns,"nifty_recent_momentum":nm}
    @staticmethod
    def _relative_strength(stock,market):
        n=min(len(stock),len(market),5)
        if n<2:return {"window_candles":n,"stock_return_pct":None,"nifty_return_pct":None,"relative_strength_pct":None}
        calc=lambda x:(float(x[-1]["close"])-float(x[-n]["close"]))/float(x[-n]["close"])*100; s,m=calc(stock),calc(market); return {"window_candles":n,"stock_return_pct":round(s,4),"nifty_return_pct":round(m,4),"relative_strength_pct":round(s-m,4)}
    @staticmethod
    def _volatility(values, plan):
        if not values: return {"last_completed_range": None}
        ranges = [float(c["high"]) - float(c["low"]) for c in values]
        result = {"last_completed_range": round(ranges[-1], 4)}
        for count in (5, 10):
            result[f"previous_{count}_candle_median_range"] = round(median(ranges[-(count + 1):-1]), 4) if len(ranges) > count else None
        economics = ReplayCoachDecisionContext._economics(plan)
        baseline = result["previous_10_candle_median_range"] or result["previous_5_candle_median_range"]
        result["target_distance_multiple"] = round(economics["reward"] / baseline, 4) if baseline and economics.get("reward") is not None else None
        result["stop_distance_multiple"] = round(economics["risk"] / baseline, 4) if baseline and economics.get("risk") is not None else None
        return result
    @staticmethod
    def _levels(values, entry):
        if len(values) < 2 or entry is None: return []
        tolerance = round(float(entry) * .001, 4); levels = []
        for kind, key in (("SUPPORT", "low"), ("RESISTANCE", "high")):
            for candle in values:
                price = float(candle[key]); touches = [item for item in values if abs(float(item[key]) - price) <= tolerance]
                if len(touches) >= 2:
                    centre = round(sum(float(item[key]) for item in touches) / len(touches), 4)
                    zone_lower, zone_upper = round(min(float(item[key]) for item in touches), 4), round(max(float(item[key]) for item in touches), 4)
                    sources = [{"time": item["time"], "time_semantics": "CANDLE_OPEN", "field": key.upper(), "value": round(float(item[key]), 4), "close": round(float(item["close"]), 4), "qualified": True, "reason": f"{key.title()} is within the detected {kind.lower()} zone."} for item in touches]
                    penetrations, consecutive = [], 0
                    for item in values:
                        extreme, close = float(item[key]), float(item["close"])
                        penetrated = extreme < zone_lower if kind == "SUPPORT" else extreme > zone_upper
                        closed_beyond = close < zone_lower if kind == "SUPPORT" else close > zone_upper
                        consecutive = consecutive + 1 if closed_beyond else 0
                        if penetrated:
                            recovered = not closed_beyond
                            penetrations.append({"time": item["time"], "extreme": round(extreme, 4), "close": round(close, 4), "distance_beyond_centre": round(centre - extreme if kind == "SUPPORT" else extreme - centre, 4), "distance_beyond_zone": round(zone_lower - extreme if kind == "SUPPORT" else extreme - zone_upper, 4), "recovered_by_close": recovered, "closed_beyond_zone": closed_beyond, "invalidation_count_after": consecutive, "counts_toward_invalidation": closed_beyond, "explanation": f"Price penetrated {'below' if kind == 'SUPPORT' else 'above'} the {kind.lower()} zone" + (f" but recovered to close {'above' if kind == 'SUPPORT' else 'below'} it." if recovered else ".")})
                    # A recovered penetration is a deterministic rejection of this zone; otherwise use its outer source candle.
                    rejection = [item for item in penetrations if item["recovered_by_close"]]
                    structural = min(rejection, key=lambda item: item["extreme"]) if kind == "SUPPORT" and rejection else max(rejection, key=lambda item: item["extreme"]) if rejection else (min(sources, key=lambda item: item["value"]) if kind == "SUPPORT" else max(sources, key=lambda item: item["value"]))
                    levels.append({"level": centre, "level_type": kind, "method": f"MEAN_OF_QUALIFYING_{key.upper()}S", "zone_lower": zone_lower, "zone_upper": zone_upper, "touch_count": len(touches), "required_reactions": 2, "touch_timestamps": [item["time"] for item in touches], "source_candles": sources, "penetrations": penetrations, "invalidation_required_closes": ReplayCoachDecisionContext.STRUCTURE_INVALIDATION_CLOSES, "invalidation_consecutive_closes": max((item["invalidation_count_after"] for item in penetrations), default=0), "invalidated": any(item["invalidation_count_after"] >= ReplayCoachDecisionContext.STRUCTURE_INVALIDATION_CLOSES for item in penetrations), "structural_extreme": {"time": structural["time"], "field": key.upper(), "value": structural.get("extreme", structural.get("value")), "reason": f"Pre-entry {'rejection' if structural in rejection else 'qualifying'} {key} associated with the {kind.lower()} structure."}, "clustering_tolerance": tolerance, "distance_from_proposed_entry": round(float(entry) - price, 4), "established_before_entry": True})
                    break
        return levels
    @staticmethod
    def _economics(plan):
        entry,stop,target,side=(plan.get(k) for k in ("entry_price","stop_price","target_price","position_type"))
        if None in (entry,stop,target) or side not in ("LONG","SHORT"):return {"required_ratio":MINIMUM_REWARD_RISK_RATIO}
        risk=float(entry)-float(stop) if side=="LONG" else float(stop)-float(entry); reward=float(target)-float(entry) if side=="LONG" else float(entry)-float(target); ratio=reward/risk if risk>0 else None; maximum=reward/MINIMUM_REWARD_RISK_RATIO if reward>0 else None
        allowable=float(entry)-maximum if side=="LONG" and maximum is not None else float(entry)+maximum if maximum is not None else None
        return {"entry":entry,"stop":stop,"target":target,"risk":round(risk,4),"reward":round(reward,4),"reward_risk_ratio":round(ratio,4) if ratio is not None else None,"required_ratio":MINIMUM_REWARD_RISK_RATIO,"ratio_shortfall":round(max(0,MINIMUM_REWARD_RISK_RATIO-(ratio or 0)),4),"maximum_allowed_risk":round(maximum,4) if maximum is not None else None,"allowable_stop":round(allowable,4) if allowable is not None else None,"break_even_win_rate":round(risk/(risk+reward),4) if risk>0 and reward>0 else None,"equal_wins_to_recover_one_loss":round(risk/reward,4) if risk>0 and reward>0 else None,"take_valid":bool(ratio is not None and ratio>=MINIMUM_REWARD_RISK_RATIO)}
