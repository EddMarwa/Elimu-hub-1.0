@echo off
echo 🚀 Starting Elimu Hub with Demo
echo ================================
echo.
echo Starting server in background...
start /B python minimal_server.py
echo.
echo Waiting for server to start...
timeout /t 3 /nobreak >nul
echo.
echo Running demo...
python demo.py
echo.
echo Demo complete! Server is still running at http://localhost:8000
echo Visit http://localhost:8000/docs for interactive API
echo.
pause
