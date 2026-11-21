from backend.services.market_context_engine import calculate_market_context

def test_vwap_and_orb_use_completed_input_only():
    candles=[{"time":f"2026-09-28 09:{15+i*5:02d}:00","open":10,"high":11+i,"low":9,"close":10+i,"volume":100} for i in range(6)]
    result=calculate_market_context(candles)
    assert result["orb"] == {"high":16.0,"low":9.0}
    assert result["vwap"]["value"] > 0
    partial=calculate_market_context(candles[:5])
    assert partial["orb"] == {"high":None,"low":None}
