# utils.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database_config import SessionLocal  # Assuming SessionLocal is in database_config.py
from datetime import datetime, timedelta
import os

# Initialize CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Secret and Algorithm for encoding/decoding the token
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Set your secret key in .env or as an environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

def hash_password(password: str) -> str:
    """Hash the password."""
    return pwd_context.hash(password)

def verify_password_
