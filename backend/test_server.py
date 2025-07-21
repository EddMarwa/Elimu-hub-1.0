#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("Python path:", sys.path)
print("Backend dir:", backend_dir)

try:
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
except ImportError as e:
    print("❌ FastAPI import failed:", e)

try:
    from jose import JWTError, jwt
    print("✓ jose imported successfully")
except ImportError as e:
    print("❌ jose import failed:", e)

try:
    from passlib.context import CryptContext
    print("✓ passlib imported successfully")
except ImportError as e:
    print("❌ passlib import failed:", e)

try:
    import fitz  # PyMuPDF
    print("✓ PyMuPDF imported successfully")
except ImportError as e:
    print("❌ PyMuPDF import failed:", e)

try:
    from app.config import settings
    print("✓ app.config imported successfully")
except ImportError as e:
    print("❌ app.config import failed:", e)

# Simple FastAPI test
app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Test server is working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
