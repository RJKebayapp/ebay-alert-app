from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
import logging
import traceback

from models import User
from schemas import UserCreate, UserLogin, TokenData, Token, UserResponse
from database_config import get_async_session
from dependencies import get_current_user, create_access_token

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Environment variables with proper fallbacks
SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours default

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password for storing."""
    return pwd_context.hash(password)

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    """Register a new user."""
    try:
        logger.info(f"Attempting to register user with email: {user.email}")
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user.email))
        db_user = result.scalars().first()
        
        if db_user:
            logger.warning(f"User with email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Hash the password
        logger.info("Hashing password")
        hashed_password = get_password_hash(user.password)
        
        # Create new user
        logger.info("Creating new user")
        new_user = User(email=user.email, hashed_password=hashed_password)
        
        # Add to database
        logger.info("Adding user to database")
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"User registered successfully: {user.email}")
        return {"id": new_user.id, "email": new_user.email}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in register_user: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_session)):
    """Authenticate a user and return a JWT token."""
    try:
        logger.info(f"Login attempt for user: {user.email}")
        
        # Find the user
        result = await db.execute(select(User).where(User.email == user.email))
        db_user = result.scalars().first()
        
        # Verify user exists and password is correct
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"Invalid login attempt for: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in login: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Simple endpoint for testing authentication without database operations
@router.post("/register-minimal")
async def register_user_minimal(user_data: dict):
    """Minimal registration endpoint for testing."""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        
        # Log incoming data
        logger.info(f"Attempting minimal registration for: {email}")
        
        # Just return success without doing any database operations
        return {
            "status": "success", 
            "message": "Registration endpoint reached", 
            "email": email
        }
        
    except Exception as e:
        logger.error(f"Error in minimal registration: {str(e)}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}
