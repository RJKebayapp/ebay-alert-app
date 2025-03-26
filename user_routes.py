from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from dependencies import get_current_user
from database_config import get_async_session
from models import User
from schemas import UserUpdate, UserOut

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/me", response_model=UserOut)
async def read_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the current user's profile.
    """
    return current_user

@router.put("/me/update", response_model=UserOut)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update the current user's profile.
    You can update email and/or password.
    """
    # If a new email is provided and it's different, check if it's already registered.
    if user_update.email and user_update.email != current_user.email:
        result = await session.execute(select(User).where(User.email == user_update.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email

    # If a new password is provided, hash it.
    if user_update.password:
        hashed_password = pwd_context.hash(user_update.password)
        current_user.hashed_password = hashed_password

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user

from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database_config import get_async_session
from dependencies import get_current_user
from models import User

# Schema for updating subscription tier
class SubscriptionUpdate(BaseModel):
    subscription_tier: Literal["free", "mid", "top"]

@router.put("/me/subscription", response_model=dict)
async def update_subscription(
    update: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Update the user's subscription tier
    current_user.subscription_tier = update.subscription_tier
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "subscription_tier": current_user.subscription_tier
    }

