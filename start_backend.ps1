# Elimu Hub Backend Startup Script
Write-Host "🚀 Starting Elimu Hub Backend..." -ForegroundColor Green

# Navigate to project directory
Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Navigate to backend
Set-Location backend

# Check if GROQ_API_KEY is set
if (-not $env:GROQ_API_KEY) {
    Write-Host "⚠️  Warning: GROQ_API_KEY not set in environment" -ForegroundColor Yellow
    Write-Host "   Please set it in your .env file or environment variables" -ForegroundColor Yellow
}

# Start the server
Write-Host "🌐 Starting backend server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API docs will be available at http://localhost:8000/docs" -ForegroundColor Blue
python run_server.py
