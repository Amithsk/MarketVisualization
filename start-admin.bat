@echo off
echo ======================================
echo Starting MARKET VISUALIZATION (ADMIN)
echo ======================================

REM -------------------------------
REM 1. JOURNAL BACKEND (8001)
REM -------------------------------
start "Journal Backend (8001)" cmd /k ^
cd /d D:\MarketVisualization\TradeJournal\backend ^&^
call tradejournalenv\Scripts\activate ^&^
echo Running Journal Backend on 8001 ^&^
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

REM -------------------------------
REM 2.TRADE SETUP BACKEND (8002)
REM -------------------------------
start "Trade Setup Backend (8002)" cmd /k ^
cd /d D:\MarketVisualization\TradeSetup\ ^&^
call backend\tradesetupenv\Scripts\activate ^&^
echo Running Setup Backend on 8002 ^&^
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8002

REM -------------------------------
REM 3. INTRADAY BACKEND (8003)
REM -------------------------------
start "Intraday Backend (8003)" cmd /k ^
cd /d D:\MarketVisualization\IntradayTradeStockAnalyser ^&^
call IntradayTradeStockAnalyserenv\Scripts\activate ^&^
echo Running Intraday Backend on 8003 ^&^
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8003

REM -------------------------------
REM 4. JOURNAL FRONTEND (3001)
REM -------------------------------
start "Journal Frontend (3001)" cmd /k ^
cd /d D:\MarketVisualization\TradeJournal\frontend ^&^
echo Building Journal Frontend... ^&^
npm run build ^&^
echo Starting Journal Frontend... ^&^
npm run start

REM -------------------------------
REM 5.TRADE SETUP FRONTEND (3002)
REM -------------------------------
start "Trade Setup Frontend (3002)" cmd /k ^
cd /d D:\MarketVisualization\TradeSetup\frontend ^&^
echo Building Trade Setup Frontend... ^&^
npm run build ^&^
echo Starting Trade Setup Frontend... ^&^
npm run start

REM -------------------------------
REM 6. INTRADAY FRONTEND (3003)
REM -------------------------------
start "Intraday Frontend (3003)" cmd /k ^
cd /d D:\MarketVisualization\IntradayTradeStockAnalyser\frontend ^&^
echo Starting Intraday Frontend on 3003... ^&^
npm run dev -- --port 3003

REM -------------------------------
REM 7. STREAMLIT (8501)
REM -------------------------------
start "Streamlit (8501)" cmd /k ^
cd /d D:\MarketVisualization\ ^&^
call visualenv\Scripts\activate ^&^
cd Code ^&^
echo Running Streamlit on 8501 (base path: /viz) ^&^
streamlit run app.py --server.port 8501 --server.headless true --server.baseUrlPath viz

REM -------------------------------
REM 8. NGINX
REM -------------------------------
start "NGINX" cmd /k ^
cd /d D:\Tool\nginx ^&^
echo Starting NGINX cleanly... ^&^
taskkill /IM nginx.exe /F ^>nul 2^>^&1 ^&^
nginx.exe

REM -------------------------------
REM 9. NGROK
REM -------------------------------
start "NGROK (Public URL)" cmd /k ^
cd /d D:\Tool\ngrok ^&^
echo Starting NGROK Tunnel ^&^
ngrok.exe http 80

echo ======================================
echo All services triggered.
echo ======================================
pause
