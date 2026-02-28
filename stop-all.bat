@echo off
echo ======================================
echo Stopping MARKET VISUALIZATION services
echo ======================================

REM --------------------------------------
REM 1. Gracefully stop NGINX
REM --------------------------------------
echo [1/6] Stopping NGINX...
cd /d D:\Tool\nginx
taskkill /IM nginx.exe /F >nul 2>&1

REM --------------------------------------
REM 2. Stop NGROK
REM --------------------------------------
echo [2/6] Stopping NGROK...
taskkill /IM ngrok.exe /F >nul 2>&1

REM --------------------------------------
REM 3. Stop STREAMLIT
REM --------------------------------------
echo [3/6] Stopping Streamlit...
taskkill /IM streamlit.exe /F >nul 2>&1

REM --------------------------------------
REM 4. Stop UVICORN (reload runs via python)
REM --------------------------------------
echo [4/6] Stopping FastAPI Backends...
taskkill /IM python.exe /F >nul 2>&1

REM --------------------------------------
REM 5. Stop React Dev Servers (Next.js)
REM --------------------------------------
echo [5/6] Stopping React Dev Servers...
taskkill /IM node.exe /F >nul 2>&1

REM --------------------------------------
REM 6. Verify Ports Are Cleared
REM --------------------------------------
echo ======================================
echo [6/6] Verifying ports...
echo ======================================

for %%P in (8001 8002 3001 3002 8501 80) do (
    echo Checking port %%P...
    netstat -ano | findstr :%%P
)

echo ======================================
echo Stop sequence complete.
echo ======================================
pause