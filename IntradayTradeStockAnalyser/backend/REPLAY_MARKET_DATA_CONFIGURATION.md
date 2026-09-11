# Replay market-data configuration

Replay calls the existing Raspberry Pi market-data API. Before starting the
Intraday Trade Stock Analyser backend, set this process environment variable:

```powershell
$env:ZERODHA_MARKET_DATA_BASE_URL = "http://<PI_ADDRESS>:8001"
.\backend\IntradayTradeStockAnalyserenv\Scripts\uvicorn.exe backend.app:app --reload --host 127.0.0.1 --port 8003
```

Do not use `http://127.0.0.1:8001`; on this workstation that port belongs to
TradeJournal, not the Pi service. The base URL must not include credentials.

For Replay input `SBIN` and `2026-09-11`, the backend calls:

```text
http://<PI_ADDRESS>:8001/zerodha/symbol/historical-candles?symbol=NSE:SBIN&trade_date=2026-09-11
```

The configuration is intentionally required for Replay. A missing or malformed
value returns the existing `ZERODHA_UNAVAILABLE`/503 contract, rather than
silently calling a localhost fallback.
