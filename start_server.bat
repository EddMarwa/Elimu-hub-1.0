@echo off
echo =========================================
echo    🚀 Starting Elimu Hub Knowledge Base
echo =========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\pip install fastapi uvicorn python-multipart requests
    pause
    exit /b 1
)

echo 📚 Starting Elimu Hub Minimal Server...
echo 🔗 API will be available at: http://localhost:8000
echo 📖 Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
.venv\Scripts\python.exe minimal_server.py

echo.
echo 👋 Server stopped. Press any key to exit...
pause >nul
