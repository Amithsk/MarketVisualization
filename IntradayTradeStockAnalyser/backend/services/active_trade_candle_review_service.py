"""Completed-candle review; Trade Effect is deterministic execution evidence."""
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import isfinite

class ActiveTradeCandleReviewService:
    VERSION="active_trade_candle_review_v5"; INTERVAL=timedelta(minutes=5); TICK=.0001
    @staticmethod
    def _t(v):
        try:return datetime.fromisoformat(str(v).replace("Z","+00:00"))
        except (TypeError,ValueError):return None
    @staticmethod
    def _n(v):
        try:v=float(v);return v if isfinite(v) else None
        except (TypeError,ValueError):return None
    @staticmethod
    def _d(v):
        try:return Decimal(str(v))
        except (InvalidOperation,TypeError,ValueError):return None
    @staticmethod
    def _m(v):return f"₹{v:.2f}"
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
    @classmethod
    def _effect(cls,c,side,state,events,basis_source):
        """Only describe close-vs-open-position price effect; never make a decision."""
        a=cls._o(c);q,avg=state["open_quantity"],state["weighted_average"]
        realized=sum(e.get("realized_gross_pnl") or 0 for e in events if e.get("event_type")=="EXIT")
        changes=[f"{e['event_type']} {e['quantity']} @ {cls._m(e['price'])}: open {e['open_quantity_before']} → {e['open_quantity_after']}" for e in events]
        basis,close=cls._d(avg),cls._d(a["close"] if a else None)
        if side not in ("LONG","SHORT") or not q or basis is None or close is None:
            return {"trade_side":side if side in ("LONG","SHORT") else None,"basis_source":"UNAVAILABLE","basis_price":None,"candle_close":float(close) if close is not None else None,"movement_per_share_signed":None,"movement_classification":"UNAVAILABLE","open_quantity":q or 0,"gross_unrealized_pnl":None,"costs_included":False,"realized_gross_pnl":realized,"execution_changes":changes,"execution_details":events,"calculation_lines":[{"label":"Basis","formula":"No trustworthy open-position basis","result":"Unavailable"}],"message":"Unavailable — the open position basis could not be reconstructed safely."}
        money=lambda v:v.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
        move=money((close-basis) if side=="LONG" else (basis-close)); gross=money(move*Decimal(str(q)))
        classification="FAVOURABLE" if move>0 else "ADVERSE" if move<0 else "UNCHANGED"
        formula="candle close − basis" if side=="LONG" else "basis − candle close"
        lines=[{"label":"Basis","formula":basis_source.replace("_"," ").title(),"result":cls._m(float(basis))},{"label":"Candle close","formula":"Completed five-minute candle","result":cls._m(float(close))},{"label":"Movement","formula":f"{formula} = {cls._m(float(abs(move)))}/share {classification.lower()}","result":cls._m(float(move))},{"label":"Open quantity","formula":"Position at candle completion","result":str(q)},{"label":"Gross unrealized P&L","formula":f"{cls._m(float(move))} × {q}; costs excluded","result":cls._m(float(gross))}]
        return {"trade_side":side,"basis_source":basis_source,"basis_price":float(basis),"candle_close":float(close),"movement_per_share_signed":float(move),"movement_classification":classification,"open_quantity":q,"gross_unrealized_pnl":float(gross),"costs_included":False,"realized_gross_pnl":realized,"execution_changes":changes,"execution_details":events,"calculation_lines":lines,"message":f"{side} · {cls._m(float(basis))} → {cls._m(float(close))}; {cls._m(float(abs(move)))}/share {classification.lower()}."}
    @classmethod
    def _decision(cls,side,candle,structure,effect,stop,target,entered_during_candle):
        """Evidence-specific close-of-candle decision; no generic Coach prose."""
        o=cls._o(candle)
        if not o or side not in ("LONG","SHORT"):
            return {"classification":"WATCH","reason_codes":["EVIDENCE_UNAVAILABLE"],"message":"Decision evidence is unavailable because the completed candle or trade direction could not be established."}
        target_hit=target is not None and ((side=="LONG" and o["high"]>=target) or (side=="SHORT" and o["low"]<=target));stop_hit=stop is not None and ((side=="LONG" and o["low"]<=stop) or (side=="SHORT" and o["high"]>=stop))
        if entered_during_candle and (target_hit or stop_hit):
            return {"classification":"WATCH","reason_codes":["INTRABAR_SEQUENCE_UNKNOWN"],"message":"Target or stop may have traded in the entry candle, but OHLC does not prove that it occurred after entry."}
        if target_hit:
            extreme=o["high"] if side=="LONG" else o["low"];penetration=(extreme-target) if side=="LONG" else (target-extreme)
            return {"classification":"EXIT","reason_codes":["TARGET_REACHED"],"message":f"The {side} target of {cls._m(target)} was reached; the candle {'high' if side=='LONG' else 'low'} of {cls._m(extreme)} moved {cls._m(penetration)} beyond the target."}
        if stop_hit:
            extreme=o["low"] if side=="LONG" else o["high"];penetration=(stop-extreme) if side=="LONG" else (extreme-stop)
            return {"classification":"EXIT","reason_codes":["STOP_REACHED"],"message":f"The {side} stop of {cls._m(stop)} was reached; the candle {'low' if side=='LONG' else 'high'} of {cls._m(extreme)} moved {cls._m(penetration)} beyond the stop."}
        favourable=effect.get("movement_classification")=="FAVOURABLE";supported=structure==("HH_HL" if side=="LONG" else "LH_LL")
        if favourable and supported:
            return {"classification":"HOLD","reason_codes":["FAVOURABLE_MOVEMENT","STRUCTURE_INTACT"],"message":f"The {side} remained supported: price moved {cls._m(abs(effect['movement_per_share_signed']))} per share in the favourable direction, {'bullish' if side=='LONG' else 'bearish'} structure remained intact and no exit condition was reached."}
        return {"classification":"WATCH","reason_codes":["FOLLOW_THROUGH_WEAKENED" if not supported else "MOVEMENT_NOT_FAVOURABLE"],"message":f"The {side} remained valid, but {'price movement was adverse or unchanged' if not favourable else 'follow-through weakened'}. No stop or structural invalidation was reached."}
    @classmethod
    def build(cls,stock,market,trade,plan,execution_history=None):
        history=sorted(execution_history or [],key=lambda e:(e.get("execution_timestamp",""),e.get("sequence",0)));first=cls._t(history[0].get("execution_timestamp")) if history else cls._t(trade.get("entry_timestamp"));final=cls._t(trade.get("exit_timestamp"))
        if history and history[-1].get("event_type")=="EXIT" and history[-1].get("open_quantity_after")==0:final=cls._t(history[-1].get("execution_timestamp"))
        side=(plan.get("position_type") or ("LONG" if trade.get("side")=="BUY" else "SHORT")).upper();out={"version":cls.VERSION,"trade_side":side,"entry_timestamp":first.isoformat() if first else None,"exit_timestamp":final.isoformat() if final else None,"timestamp_semantics":"CANDLE_START_TIME; [start, end) assigns an exact boundary fill to the next candle","formula_key":"O = Open · H = High · L = Low · C = Close","items":[],"final_exit":{"timestamp":final.isoformat() if final else None},"summary":{"eligible_completed_candles":0}}
        if not first or not final:return cls._empty(out)
        out["coach_exit_signal"]=None
        rows=sorted(((cls._t(c.get("time")),c) for c in stock if cls._t(c.get("time"))),key=lambda x:x[0]);mi={cls._t(c.get("time")):c for c in market if cls._t(c.get("time"))}
        for i,(start,c) in enumerate(rows):
            complete=start+cls.INTERVAL
            if complete<=first or complete>final:continue
            events=[e for e in history if (t:=cls._t(e.get("execution_timestamp"))) and start<=t<complete];prior=[e for e in history if (t:=cls._t(e.get("execution_timestamp"))) and t<complete];last=prior[-1] if prior else None
            state={"open_quantity":last.get("open_quantity_after",0) if last else trade.get("quantity",0),"weighted_average":last.get("weighted_average_after") if last else trade.get("entry_price")};source="ORIGINAL_EXECUTED_ENTRY" if not history else ("JOURNAL_WEIGHTED_AVERAGE" if last and last.get("position_snapshot_source")=="JOURNAL" else "RECONSTRUCTED_EXECUTION_HISTORY")
            s=cls._s(c,rows[i-1][1] if i else None);mc=mi.get(start);ms=cls._s(mc,mi.get(rows[i-1][0]) if i and mc else None) if mc else None;a=cls._o(c)
            behaviour={"classification":s,"calculation_lines":[{"label":"Completed stock candle","formula":"OHLC at candle close","result":s}],"message":f"{s.replace('_',' + ')} completed stock candle." if a else "Stock OHLC is unavailable."};relation={"classification":"UNAVAILABLE","calculation_lines":[],"message":"Matching NIFTY candle was unavailable; no NIFTY verdict is made."} if not mc else {"classification":ms,"calculation_lines":[{"label":"Matching NIFTY candle","formula":"Same five-minute start","result":ms}],"message":f"Stock {s.replace('_',' + ')}; NIFTY {ms.replace('_',' + ')}."};effect=cls._effect(c,side,state,events,source)
            stop,target=cls._n(plan.get("stop_price")),cls._n(plan.get("target_price"));entered=start<=first<complete;decision=cls._decision(side,c,s,effect,stop,target,entered)
            out["items"].append({"completion_time":complete.isoformat(timespec="seconds"),"entered_during_candle":entered,"candle_behaviour":behaviour,"nifty_relationship":relation,"trade_effect":effect,"decision":decision});out["summary"]["eligible_completed_candles"]+=1
            if decision["classification"]=="EXIT":
                actual=final.isoformat() if final else None;signal=complete.isoformat(timespec="seconds")
                out["coach_exit_signal"]={"timestamp":signal,"reason":decision["reason_codes"][0],"actual_journal_exit_timestamp":actual,"message":f"Coach exit condition occurred at {signal}; actual Journal exit was recorded at {actual}." if actual and actual!=signal else None}
                break
        if history and history[-1].get("event_type")=="EXIT":
            event=history[-1];out["final_exit"].update({key:event.get(key) for key in ("price","quantity","open_quantity_before","open_quantity_after","realized_gross_pnl","reason","note")});out["final_exit"]["message"]="Final exit is assessed at its fill time; later OHLC in that candle is excluded."
        return out if out["items"] else cls._empty(out)
    @staticmethod
    def _empty(out):
        out["items"]=[{"completion_time":None,"candle_behaviour":{"message":"No completed candle was eligible for review."},"nifty_relationship":{"message":"NIFTY relationship unavailable.","calculation_lines":[]},"trade_effect":{"trade_side":None,"basis_source":"UNAVAILABLE","basis_price":None,"candle_close":None,"movement_per_share_signed":None,"movement_classification":"UNAVAILABLE","open_quantity":0,"gross_unrealized_pnl":None,"costs_included":False,"message":"Unavailable — the open position basis could not be reconstructed safely.","calculation_lines":[]},"decision":{"classification":"NO_COMPLETED_CANDLE"}}];return out
