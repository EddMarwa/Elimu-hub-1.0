#!/usr/bin/env python3
"""
FastAPI Backend Server Startup Script
"""
import sys
import os
import uvicorn

# Ensure we're in the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Add the backend directory to Python path  
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print(f"Starting server from: {backend_dir}")
print(f"Python path includes: {backend_dir}")

if __name__ == "__main__":
    # Import the app from the correct location
    from app.main import app
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        reload=True,
        reload_dirs=[backend_dir]
    )
