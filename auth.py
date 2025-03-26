from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import jwt
import os

from models import User
from schemas import UserCreate, UserLogin
from database_config import get_async_session

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  # Make sure to set this in .env
ALGORITHM = "HS256"

@router.post("/register")
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

@router.post("/login")
async def login(user: UserLogin, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()

    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": db_user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
