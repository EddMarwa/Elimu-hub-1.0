@echo off
echo 🚀 Starting Elimu Hub - Full Stack
echo ===================================
echo.

REM Check if backend is already running
echo Checking if backend is running...
for /f %%i in ('powershell -command "(Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).Count"') do set backend_running=%%i

if "%backend_running%"=="0" (
    echo Starting backend server...
    cd /d "%~dp0"
    start "Backend Server" cmd /k "python minimal_server.py"
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ Backend already running on port 8000
)

REM Check if frontend is already running
echo Checking if frontend is running...
for /f %%i in ('powershell -command "(Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue).Count"') do set frontend_running=%%i

if "%frontend_running%"=="0" (
    echo Starting frontend server...
    cd /d "%~dp0frontend"
    start "Frontend Server" cmd /k "npm run dev"
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ Frontend already running on port 3000
)

echo.
echo 🎉 Elimu Hub is starting up!
echo.
echo 🔗 Frontend: http://localhost:3000
echo 🔗 Backend API: http://localhost:8000
echo 🔗 API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the frontend...
pause >nul

start http://localhost:3000
