"""Deterministic active-trade candle calculations; timestamps are candle starts."""
from datetime import datetime, timedelta
from math import isfinite

class ActiveTradeCandleReviewService:
    VERSION="active_trade_candle_review_v2"; INTERVAL=timedelta(minutes=5); TICK=.0001
    @staticmethod
    def _t(v):
        try:return datetime.fromisoformat(str(v).replace("Z","+00:00"))
        except (TypeError,ValueError):return None
    @staticmethod
    def _n(v):
        try:v=float(v);return v if isfinite(v) else None
        except (TypeError,ValueError):return None
    @classmethod
    def _o(cls,c):
        try:
            d={x:cls._n(c[x]) for x in ("open","high","low","close")};return d if all(v is not None for v in d.values()) else None
        except (TypeError,KeyError):return None
    @classmethod
    def _s(cls,c,p):
        a,b=cls._o(c),cls._o(p)
        if not a or not b:return "UNCHANGED_OR_INSUFFICIENT"
        h,l=a["high"]-b["high"],a["low"]-b["low"]
        if a["high"]<=b["high"]+cls.TICK and a["low"]>=b["low"]-cls.TICK:return "INSIDE_RANGE"
        if h>cls.TICK and l>cls.TICK:return "HH_HL"
        if h<-cls.TICK and l<-cls.TICK:return "LH_LL"
        if h>cls.TICK and l<-cls.TICK:return "HH_LL"
        if h<-cls.TICK and l>cls.TICK:return "LH_HL"
        return "UNCHANGED_OR_INSUFFICIENT"
    @staticmethod
    def _pct(a,b):return round(a/b*100,4) if b not in (None,0) else None
    @staticmethod
    def _m(v):return f"₹{v:.2f}"
    @classmethod
    def _e(cls,c,p):
        a,b=cls._o(c),cls._o(p)
        if not a:return {"calculation_lines":[]}
        r=a["high"]-a["low"];body=abs(a["close"]-a["open"]);lw=min(a["open"],a["close"])-a["low"];uw=a["high"]-max(a["open"],a["close"]);change=a["close"]-b["close"] if b else None;pr=b["high"]-b["low"] if b else None
        high=a["close"]-b["high"] if b and a["close"]>b["high"]+cls.TICK else None;low=b["low"]-a["close"] if b and a["close"]<b["low"]-cls.TICK else None
        lines=[{"label":"Range","formula":"H − L","result":cls._m(r)},{"label":"Body","formula":"|C − O|","result":cls._m(body)}]
        if r>cls.TICK:lines += [{"label":"Body strength","formula":"Body ÷ Range × 100","result":f"{cls._pct(body,r):.1f}%"},{"label":"Close position","formula":"(C − L) ÷ Range × 100","result":f"{cls._pct(a['close']-a['low'],r):.1f}%"}]
        if b:lines.append({"label":"Close movement","formula":"(Current C − Previous C) ÷ Previous C × 100","result":f"{cls._pct(change,b['close']):+.2f}%"})
        if lw>cls.TICK:lines.append({"label":"Lower wick","formula":"min(O, C) − L","result":cls._m(lw)})
        if uw>cls.TICK:lines.append({"label":"Upper wick","formula":"H − max(O, C)","result":cls._m(uw)})
        if high is not None:lines.append({"label":"Previous-high break","formula":"Current C − Previous H","result":cls._m(high)})
        if low is not None:lines.append({"label":"Previous-low break","formula":"Previous L − Current C","result":cls._m(low)})
        if pr and pr>cls.TICK:lines.append({"label":"Range expansion","formula":"Current Range ÷ Previous Range","result":f"{r/pr:.2f}×"})
        return {"range":r,"body":body,"body_pct":cls._pct(body,r),"close_change_pct":cls._pct(change,b['close']) if b else None,"close_position_pct":cls._pct(a['close']-a['low'],r),"lower_wick":lw,"lower_wick_pct":cls._pct(lw,r),"upper_wick":uw,"upper_wick_pct":cls._pct(uw,r),"previous_high_break_retained":high,"previous_low_break_retained":low,"range_expansion_ratio":round(r/pr,4) if pr and pr>cls.TICK else None,"calculation_lines":lines}
    @classmethod
    def build(cls,stock,market,trade,plan):
        entry,exit=cls._t(trade.get("entry_timestamp")),cls._t(trade.get("exit_timestamp"));side=(plan.get("position_type") or ("LONG" if trade.get("side")=="BUY" else "SHORT")).upper();out={"version":cls.VERSION,"trade_side":side,"entry_timestamp":trade.get("entry_timestamp"),"exit_timestamp":trade.get("exit_timestamp"),"timestamp_semantics":"CANDLE_START_TIME","index_instrument":"NIFTY_FUTURES","formula_key":"O = Open · H = High · L = Low · C = Close","summary":{"eligible_completed_candles":0,"hold_count":0,"watch_count":0,"exit_count":0},"items":[]}
        rows=[(cls._t(c.get("time")),c) for c in stock];rows=[x for x in rows if x[0]];mi={cls._t(c.get("time")):c for c in market if cls._t(c.get("time"))}
        if not entry or not exit:return cls._empty(out)
        for i,(start,c) in enumerate(rows):
            complete=start+cls.INTERVAL
            if not complete>entry or not complete<=exit:continue
            p=rows[i-1][1] if i else None;e=cls._e(c,p);s=cls._s(c,p);mc=mi.get(start);me=cls._e(mc,mi.get(rows[i-1][0]) if i else None) if mc else None;ms=cls._s(mc,mi.get(rows[i-1][0]) if i and mc else None)
            change=e.get("close_change_pct");pos=e.get("close_position_pct");wick=e.get("lower_wick_pct") or 0;direction="continued downward direction" if s=="LH_LL" else "continued upward direction" if s=="HH_HL" else "mixed direction";detail="A material lower wick shows the downward attempt was partly rejected." if wick>=35 else "The break of the previous range was retained through the close." if e.get("previous_low_break_retained") is not None or e.get("previous_high_break_retained") is not None else "The candle did not retain a clear range break."
            behaviour={"classification":"REJECTED" if wick>=35 else "EFFECTIVE" if s in ("HH_HL","LH_LL") else "MIXED","message":f"{s.replace('_',' + ')} with a {change:+.2f}% close movement indicates {direction}. The {e.get('body_pct') or 0:.1f}% body closed {'at the candle low' if (pos or 100)<=1 else 'at the candle high' if (pos or 0)>=99 else 'within the range'}. {detail}"}
            if not mc:rel={"classification":"UNAVAILABLE","stock_close_change_pct":change,"nifty_close_change_pct":None,"calculation_lines":[],"message":"Matching NIFTY candle was unavailable."}
            else:
                state="ALIGNED_LONG" if s==ms=="HH_HL" else "ALIGNED_SHORT" if s==ms=="LH_LL" else "STOCK_WEAK_VS_NIFTY" if s=="LH_LL" and ms=="HH_HL" else "STOCK_STRONG_VS_NIFTY" if s=="HH_HL" and ms=="LH_LL" else "MIXED";rel={"classification":state,"stock_close_change_pct":change,"nifty_close_change_pct":me.get("close_change_pct"),"stock_retained_break":e.get("previous_low_break_retained") or e.get("previous_high_break_retained"),"nifty_retained_break":me.get("previous_low_break_retained") or me.get("previous_high_break_retained"),"calculation_lines":e["calculation_lines"]+me["calculation_lines"],"message":f"Stock {change:+.2f}% and NIFTY {me.get('close_change_pct'):+.2f}%; stock {s.replace('_',' + ')} and NIFTY {ms.replace('_',' + ')}. The movement was {state.replace('_',' ').lower()} for the {side}."}
            a=cls._o(c);move=(a["close"]-cls._n(trade.get("entry_price"))) if side=="LONG" else (cls._n(trade.get("entry_price"))-a["close"]);favour=move>=-cls.TICK;effect={"trade_side":side,"movement_from_entry":move,"movement_classification":"FAVOURABLE" if favour else "ADVERSE","calculation_lines":[{"label":"Movement from entry","formula":"Current C − Entry" if side=="LONG" else "Entry − Current C","result":cls._m(abs(move))}],"message":f"The {side} moved {cls._m(abs(move))} per share {'in the favourable direction' if favour else 'against the trade'}, excluding costs."}
            target,stop=cls._n(plan.get("target_price")),cls._n(plan.get("stop_price"));hit_t=target is not None and ((side=="LONG" and a["high"]>=target-cls.TICK) or (side=="SHORT" and a["low"]<=target+cls.TICK));hit_s=stop is not None and ((side=="LONG" and a["low"]<=stop+cls.TICK) or (side=="SHORT" and a["high"]>=stop-cls.TICK));decision,reasons=("EXIT",["TARGET_REACHED"]) if hit_t else ("EXIT",["STOP_REACHED"]) if hit_s else ("HOLD",["FAVOURABLE_STRUCTURE"]) if (side=="LONG" and s=="HH_HL") or (side=="SHORT" and s=="LH_LL") else ("WATCH",["MIXED_OR_ADVERSE_EVIDENCE"])
            out["items"].append({"completion_time":complete.isoformat(timespec="seconds"),"stock_structure":s,"candle_effectiveness":e,"candle_behaviour":behaviour,"nifty_relationship":rel,"trade_effect":effect,"decision":{"classification":decision,"reason_codes":reasons}});out["summary"]["eligible_completed_candles"]+=1;out["summary"][f"{decision.lower()}_count"]+=1
        return out if out["items"] else cls._empty(out)
    @staticmethod
    def _empty(out):
        out["items"]=[{"completion_time":None,"candle_behaviour":{"message":"No completed five-minute candle was available for an evidence-based management decision."},"nifty_relationship":{"classification":"UNAVAILABLE","message":"NIFTY relationship unavailable.","calculation_lines":[]},"trade_effect":{"message":"No completed candle.","calculation_lines":[]},"decision":{"classification":"NO_COMPLETED_CANDLE","reason_codes":["NO_COMPLETED_CANDLE"]}}];return out
