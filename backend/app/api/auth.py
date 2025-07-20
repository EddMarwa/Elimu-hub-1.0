from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.models import User, UserCreate, UserLogin, UserResponse, Token
from app.auth.utils import get_password_hash, authenticate_user, create_access_token
from app.auth.dependencies import get_current_active_user
from app.utils.logger import logger
from datetime import timedelta
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    try:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            created_at=db_user.created_at,
            last_login=db_user.last_login
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    logger.info(f"Login attempt for email: {user_credentials.email}")
    
    user_data = authenticate_user(user_credentials.email, user_credentials.password, db)
    if not user_data:
        logger.warning(f"Failed login attempt for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"], "user_id": user_data["id"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in successfully: {user_data['email']}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should discard token)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"} 