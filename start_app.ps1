# Elimu Hub Complete Startup Script
Write-Host "🎯 Starting Complete Elimu Hub Application..." -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta

# Navigate to project directory
Set-Location $PSScriptRoot

Write-Host "🔧 Setting up environment..." -ForegroundColor Yellow

# Start backend in background
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Green
Start-Process PowerShell -ArgumentList "-NoExit", "-File", "start_backend.ps1"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start frontend
Write-Host "⚡ Starting Frontend Server..." -ForegroundColor Cyan
Start-Process PowerShell -ArgumentList "-NoExit", "-File", "start_frontend.ps1"

Write-Host ""
Write-Host "✅ Elimu Hub is starting up!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🚀 Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "⏳ Please wait a few moments for both servers to fully initialize..." -ForegroundColor Yellow
