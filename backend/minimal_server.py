#!/usr/bin/env python3
"""
Minimal Backend Server for Testing
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import hashlib
import uvicorn
import os

# Initialize FastAPI
app = FastAPI(title="Elimu Hub API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Settings
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user database - use the admin user we created
mock_users = {
    "admin@elimuhub.com": {
        "id": 1,
        "email": "admin@elimuhub.com",
        "username": "Elimuhub",
        "hashed_password": pwd_context.hash("Elimuhub2025#"),  # Hash the password
        "is_active": True,
        "is_admin": True
    }
}

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class HealthResponse(BaseModel):
    status: str
    timestamp: float

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str):
    user = mock_users.get(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().timestamp()}

@app.get("/")
async def root():
    return {"message": "Elimu Hub API is running", "version": "1.0.0"}

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Authenticate user
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["email"]})
    
    # Return user info (exclude password)
    user_info = {k: v for k, v in user.items() if k != "hashed_password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_info
    }

@app.get("/api/v1/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = mock_users.get(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Return user info (exclude password)
    user_info = {k: v for k, v in user.items() if k != "hashed_password"}
    return user_info

if __name__ == "__main__":
    print("🚀 Starting Elimu Hub Backend Server...")
    print("📍 Server running at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("🔑 Admin login: admin@elimuhub.com / Elimuhub2025#")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False  # Disable reload to avoid import issues
    )
