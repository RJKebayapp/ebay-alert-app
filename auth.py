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
import sys

from models import User
from schemas import UserCreate, UserLogin, TokenData, Token, UserResponse
from database_config import get_async_session

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
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

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a new JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db: AsyncSession = Depends(get_async_session)):
    """Decode and verify the JWT token to get the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    try:
        result = await db.execute(select(User).where(User.email == token_data.email))
        user = result.scalars().first()
        if user is None:
            raise credentials_exception
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_current_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    """Register a new user."""
    try:
        logger.info(f"Starting registration process for email: {user.email}")
        
        # Check if user already exists
        logger.info(f"Checking if user exists: {user.email}")
        query = select(User).where(User.email == user.email)
        logger.info(f"Executing query: {query}")
        
        result = await db.execute(query)
        db_user = result.scalars().first()
        
        if db_user:
            logger.warning(f"User already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Hash the password
        logger.info("Hashing password")
        hashed_password = get_password_hash(user.password)
        
        # Create new user
        logger.info(f"Creating new user object for: {user.email}")
        new_user = User(email=user.email, hashed_password=hashed_password)
        
        # Add to database
        logger.info(f"Adding user to database: {user.email}")
        db.add(new_user)
        
        logger.info(f"Committing transaction for: {user.email}")
        await db.commit()
        
        logger.info(f"Refreshing user object for: {user.email}")
        await db.refresh(new_user)
        
        logger.info(f"User registered successfully: {user.email}")
        return {"id": new_user.id, "email": new_user.email}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in register_user: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full exception: {repr(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full exception: {repr(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_session)):
    """Authenticate a user and return a JWT token."""
    try:
        logger.info(f"Login attempt for user: {user.email}")
        
        # Find the user
        logger.info(f"Executing query to find user: {user.email}")
        result = await db.execute(select(User).where(User.email == user.email))
        db_user = result.scalars().first()
        
        # Verify user exists and password is correct
        if not db_user:
            logger.warning(f"User not found: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        logger.info(f"Verifying password for: {user.email}")
        if not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"Invalid password for: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Create access token
        logger.info(f"Creating access token for: {user.email}")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in login: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full exception: {repr(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full exception: {repr(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
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
