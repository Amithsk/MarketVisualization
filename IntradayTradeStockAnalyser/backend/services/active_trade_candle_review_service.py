"""Completed-candle management review for a Journal position."""
from datetime import datetime, timedelta
from math import isfinite

class ActiveTradeCandleReviewService:
    VERSION="active_trade_candle_review_v3"; INTERVAL=timedelta(minutes=5); TICK=.0001
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
        if a["high"]<=b["high"]+cls.TICK and a["low"]>=b["low"]-cls.TICK:return "INSIDE_RANGE"
        if a["high"]>b["high"]+cls.TICK and a["low"]>b["low"]+cls.TICK:return "HH_HL"
        if a["high"]<b["high"]-cls.TICK and a["low"]<b["low"]-cls.TICK:return "LH_LL"
        return "MIXED"
    @staticmethod
    def _m(v):return f"₹{v:.2f}"
    @classmethod
    def _effect(cls,c,side,state,events):
        a=cls._o(c);q,avg=state["open_quantity"],state["weighted_average"]
        unrealized=None if not q or avg is None else ((a["close"]-avg) if side=="LONG" else (avg-a["close"]))*q
        realized=sum(e.get("realized_gross_pnl") or 0 for e in events if e["event_type"]=="EXIT")
        changes=[f"{e['event_type']} {e['quantity']} @ {cls._m(e['price'])}: {e['open_quantity_before']} → {e['open_quantity_after']}" for e in events]
        lines=[]
        if q and avg is not None:lines += [{"label":"Open quantity at close","formula":"Journal position snapshot","result":str(q)},{"label":"Weighted average at close","formula":"Journal weighted average","result":cls._m(avg)}]
        if realized:lines.append({"label":"Realized gross P&L in candle","formula":"Exit versus pre-exit average × quantity","result":cls._m(realized)})
        if unrealized is not None:lines.append({"label":"Unrealized gross P&L at close","formula":"(average − close) × open quantity" if side=="SHORT" else "(close − average) × open quantity","result":cls._m(unrealized)})
        msg="No open shares at candle close." if not q else f"{q} {side} shares remained at average {cls._m(avg)}; unrealized gross P&L at close was {cls._m(unrealized)}."
        if changes:msg="; ".join(changes)+". "+msg
        return {"open_quantity":q,"weighted_average":avg,"realized_gross_pnl":realized,"unrealized_gross_pnl":unrealized,"execution_changes":changes,"execution_details":events,"calculation_lines":lines,"message":msg}
    @classmethod
    def build(cls,stock,market,trade,plan,execution_history=None):
        history=execution_history or []; first=cls._t(history[0].get("execution_timestamp")) if history else cls._t(trade.get("entry_timestamp")); final=cls._t(trade.get("exit_timestamp"))
        if history and history[-1].get("event_type")=="EXIT" and history[-1].get("open_quantity_after")==0:final=cls._t(history[-1].get("execution_timestamp"))
        side=(plan.get("position_type") or ("LONG" if trade.get("side")=="BUY" else "SHORT")).upper();out={"version":cls.VERSION,"trade_side":side,"entry_timestamp":first.isoformat() if first else None,"exit_timestamp":final.isoformat() if final else None,"timestamp_semantics":"CANDLE_START_TIME","formula_key":"O = Open · H = High · L = Low · C = Close","items":[],"final_exit":{"timestamp":final.isoformat() if final else None},"summary":{"eligible_completed_candles":0}}
        if not first or not final:return cls._empty(out)
        rows=[(cls._t(c.get("time")),c) for c in stock];rows=[x for x in rows if x[0]];mi={cls._t(c.get("time")):c for c in market if cls._t(c.get("time"))}
        for i,(start,c) in enumerate(rows):
            complete=start+cls.INTERVAL
            # Exact-boundary fills belong to the next candle. Intrabar final exits do not use later OHLC.
            if complete<=first or complete>final:continue
            events=[e for e in history if (t:=cls._t(e.get("execution_timestamp"))) and start<=t<complete]
            before_close=[e for e in history if (t:=cls._t(e.get("execution_timestamp"))) and t<complete];last=before_close[-1] if before_close else None
            state={"open_quantity":last.get("open_quantity_after",0) if last else trade.get("quantity",0),"weighted_average":last.get("weighted_average_after") if last else trade.get("entry_price")}
            p=rows[i-1][1] if i else None;s=cls._s(c,p);mc=mi.get(start);ms=cls._s(mc,mi.get(rows[i-1][0]) if i and mc else None) if mc else None;a=cls._o(c)
            behaviour={"classification":s,"message":f"{s.replace('_',' + ')} completed candle." if a else "Stock OHLC is unavailable."};rel={"classification":"UNAVAILABLE","calculation_lines":[],"message":"Matching NIFTY candle was unavailable."} if not mc else {"classification":ms,"calculation_lines":[],"message":f"Stock {s.replace('_',' + ')}; NIFTY {ms.replace('_',' + ')}."}
            effect=cls._effect(c,side,state,events) if a else {"message":"Trade effect unavailable: stock OHLC is missing.","calculation_lines":[],"execution_details":events}
            stop,target=cls._n(plan.get("stop_price")),cls._n(plan.get("target_price"));hit_t=bool(a and target is not None and ((side=="LONG" and a["high"]>=target) or (side=="SHORT" and a["low"]<=target)));hit_s=bool(a and stop is not None and ((side=="LONG" and a["low"]<=stop) or (side=="SHORT" and a["high"]>=stop)));decision="EXIT" if hit_t or hit_s else "HOLD" if s==("HH_HL" if side=="LONG" else "LH_LL") else "WATCH"
            out["items"].append({"completion_time":complete.isoformat(timespec="seconds"),"entered_during_candle":start<=first<complete,"candle_behaviour":behaviour,"nifty_relationship":rel,"trade_effect":effect,"decision":{"classification":decision,"reason_codes":["TARGET_REACHED" if hit_t else "STOP_REACHED" if hit_s else "CLOSE_REVIEW"],"message":"Assessment is at candle close; fill decisions require only previously completed candles."}});out["summary"]["eligible_completed_candles"]+=1
        return out if out["items"] else cls._empty(out)
    @staticmethod
    def _empty(out):
        out["items"]=[{"completion_time":None,"candle_behaviour":{"message":"No completed candle was eligible for review."},"nifty_relationship":{"message":"NIFTY relationship unavailable.","calculation_lines":[]},"trade_effect":{"message":"No completed candle.","calculation_lines":[]},"decision":{"classification":"NO_COMPLETED_CANDLE"}}];return out
