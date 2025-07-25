# Elimu Hub Frontend Startup Script
Write-Host "⚡ Starting Elimu Hub Frontend..." -ForegroundColor Cyan

# Navigate to project directory
Set-Location $PSScriptRoot

# Navigate to frontend
Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the development server
Write-Host "🌐 Starting frontend development server..." -ForegroundColor Cyan
Write-Host "   Frontend will be available at http://localhost:3000" -ForegroundColor Green
npm run dev
