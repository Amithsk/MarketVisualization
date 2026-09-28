"""Pure completed-candle market context; no persisted or cross-symbol state."""
import logging, os
log=logging.getLogger("market_context")
DEBUG=lambda: os.getenv("MARKET_CONTEXT_DEBUG","").lower() in {"1","true","yes"}
def n(c,k):
    try:return float(c[k])
    except (KeyError,TypeError,ValueError):return None
def emit(event_kind,**v):
    if DEBUG(): log.info("[%s] %s",event_kind," ".join(f"{k}={v[k]}" for k in v))
def zone(p,t,kind,time): return {"zone_low":p-t,"zone_high":p+t,"status":"PROVISIONAL","reaction_count":0,"volume_confirmation":None,"created_at":time,"confirmed_at":None,"kind":kind,"inside":False,"left":False,"window":0,"volumes":[],"breaks":0}
def public(z): return {k:round(v,4) if isinstance(v,float) else v for k,v in z.items() if k in {"zone_low","zone_high","status","reaction_count","volume_confirmation","created_at","confirmed_at"}}
def calculate_market_context(candles,instrument="UNKNOWN"):
    cs=[c for c in candles if all(n(c,k)!=None for k in ("high","low","close","volume"))]
    if not cs:return {"current_price":None,"vwap":None,"orb":{"high":None,"low":None},"support":None,"resistance":None}
    cur=n(cs[-1],"close"); pv=sum(((n(c,"high")+n(c,"low")+n(c,"close"))/3)*n(c,"volume") for c in cs); vol=sum(n(c,"volume") for c in cs); vw=pv/vol if vol else None
    vwap=None if vw is None else {"value":round(vw,4),"distance":round(vw-cur,4),"position":"ABOVE" if cur>vw else "BELOW" if cur<vw else "AT"}
    b=len(cs)//6; block=cs[(b-1)*6:b*6] if b else []; orb={"high":max([n(c,"high") for c in block],default=None),"low":min([n(c,"low") for c in block],default=None)}
    emit("MARKET_CONTEXT",instrument=instrument,candle_count=len(cs),last_candle=cs[-1].get("time"),current_price=cur);emit("VWAP",instrument=instrument,cumulative_price_volume=round(pv,4),cumulative_volume=vol,vwap=vw,position=vwap["position"] if vwap else None);emit("ORB",instrument=instrument,orb_high=orb["high"],orb_low=orb["low"],completed_blocks=b)
    zones=[];swing_candidates=0;confirmed_swings=0
    for i,c in enumerate(cs):
        rng=sum(n(x,"high")-n(x,"low") for x in cs[max(0,i-6):i])/max(1,len(cs[max(0,i-6):i])); tol=rng*.35; h,l=n(c,"high"),n(c,"low")
        created_now=[]
        if i>=2:
            swing_candidates+=(h>n(cs[i-1],"high") and h>n(cs[i-2],"high"))+(l<n(cs[i-1],"low") and l<n(cs[i-2],"low"))
        if i>=4:
            swing=cs[i-2];sh,sl=n(swing,"high"),n(swing,"low")
            for p,kind,ok in [(sh,"RESISTANCE",sh>n(cs[i-3],"high") and sh>n(cs[i-4],"high") and sh>=n(cs[i-1],"high") and sh>=h),(sl,"SUPPORT",sl<n(cs[i-3],"low") and sl<n(cs[i-4],"low") and sl<=n(cs[i-1],"low") and sl<=l)]:
                if ok:
                    confirmed_swings+=1
                    z=next((x for x in zones if x["kind"]==kind and p>=x["zone_low"]-tol and p<=x["zone_high"]+tol and max(x["zone_high"],p)-min(x["zone_low"],p)<=rng*2),None)
                    if z:z["zone_low"]=min(z["zone_low"],p);z["zone_high"]=max(z["zone_high"],p)
                    else: z=zone(p,tol,kind,c.get("time"));zones.append(z);created_now.append(z);emit("S/R ZONE",instrument=instrument,event="CREATED",zone_type=kind,price=p)
        for z in zones:
            if z in created_now: continue
            overlap=h>=z["zone_low"] and l<=z["zone_high"]
            if overlap and not z["inside"]: z["inside"]=True;z["left"]=False;z["window"]=0;z["volumes"]=[];emit("S/R INTERACTION",instrument=instrument,event="ENTER",zone=z["kind"])
            elif not overlap and z["inside"]: z["inside"]=False;z["left"]=True;z["window"]=0;emit("S/R INTERACTION",instrument=instrument,event="LEAVE",zone=z["kind"])
            elif z["left"] and z["window"]<2:
                z["window"]+=1;z["volumes"].append(n(c,"volume")); threshold=rng*.5; hit=n(c,"close")<=z["zone_low"]-threshold if z["kind"]=="RESISTANCE" else n(c,"close")>=z["zone_high"]+threshold
                if hit:
                    z["reaction_count"]+=1;z["status"]="ACTIVE" if z["reaction_count"]>=2 else "CANDIDATE";z["confirmed_at"]=c.get("time");base=sum(n(x,"volume") for x in cs[max(0,i-6):i])/max(1,len(cs[max(0,i-6):i])); rel=sum(z["volumes"])/(base*len(z["volumes"])) if base else 0;z["volume_confirmation"]="ELEVATED" if rel>=1.2 else "NORMAL" if rel>=.8 else "WEAK";z["left"]=False;emit("S/R REACTION",instrument=instrument,result="CONFIRMED",count=z["reaction_count"],status=z["status"])
                elif z["window"]==2:z["left"]=False;emit("S/R REACTION",instrument=instrument,result="NO_REACTION")
            if z["status"]=="ACTIVE":
                bad=n(c,"close")>z["zone_high"] if z["kind"]=="RESISTANCE" else n(c,"close")<z["zone_low"];z["breaks"]=z["breaks"]+1 if bad else 0
                if z["breaks"]>=2:z["status"]="BROKEN";emit("S/R INVALIDATION",instrument=instrument,status="BROKEN")
    active=[z for z in zones if z["status"]=="ACTIVE"]
    support=min([z for z in active if z["zone_high"]<cur and z["kind"]=="SUPPORT"],key=lambda z:cur-z["zone_high"],default=None); resistance=min([z for z in active if z["zone_low"]>cur and z["kind"]=="RESISTANCE"],key=lambda z:z["zone_low"]-cur,default=None)
    emit("S/R",instrument=instrument,completed_candles=len(cs),swing_candidates=swing_candidates,confirmed_swings=confirmed_swings,provisional_zones=sum(z["status"]=="PROVISIONAL" for z in zones),candidate_zones=sum(z["status"]=="CANDIDATE" for z in zones),active_zones=len(active),nearest_support=bool(support),nearest_resistance=bool(resistance))
    emit("MARKET_CONTEXT_RESULT",instrument=instrument,current=cur,vwap=vw,orb_high=orb["high"],orb_low=orb["low"],support=bool(support),resistance=bool(resistance))
    return {"current_price":cur,"vwap":vwap,"orb":orb,"support":public(support) if support else None,"resistance":public(resistance) if resistance else None,"nearest_active_support":public(support) if support else None,"nearest_active_resistance":public(resistance) if resistance else None}
