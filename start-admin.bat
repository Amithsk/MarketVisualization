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
REM 2. SETUP BACKEND (8002)
REM -------------------------------
start "Setup Backend (8002)" cmd /k ^
cd /d D:\MarketVisualization\TradeSetup\ ^&^
call backend\tradesetupenv\Scripts\activate ^&^
echo Running Setup Backend on 8002 ^&^
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8002

REM -------------------------------
REM 3. JOURNAL FRONTEND (3001)
REM -------------------------------
start "Journal Frontend (3001)" cmd /k ^
cd /d D:\MarketVisualization\TradeJournal\frontend ^&^
echo Running Journal Frontend on 3001 ^&^
npm run dev

REM -------------------------------
REM 4. SETUP FRONTEND (3002)
REM -------------------------------
start "Setup Frontend (3002)" cmd /k ^
cd /d D:\MarketVisualization\TradeSetup\frontend ^&^
echo Running Setup Frontend on 3002 ^&^
npm run dev

REM -------------------------------
REM 5. STREAMLIT (8501)
REM -------------------------------
start "Streamlit (8501)" cmd /k ^
cd /d D:\MarketVisualization\ ^&^
call visualenv\Scripts\activate ^&^
cd Code ^&^
echo Running Streamlit on 8501 ^&^
streamlit run app.py --server.port 8501

REM -------------------------------
REM 6. NGINX
REM -------------------------------
start "NGINX" cmd /k ^
cd /d D:\Tool\nginx ^&^
echo Starting NGINX ^&^
nginx.exe

REM -------------------------------
REM 7. NGROK
REM -------------------------------
start "NGROK (Public URL)" cmd /k ^
cd /d D:\Tool\ngrok ^&^
echo Starting NGROK Tunnel ^&^
ngrok.exe http 80

echo ======================================
echo All services triggered.
echo ======================================
pause