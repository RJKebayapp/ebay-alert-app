# In user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database_config import get_async_session
from dependencies import get_current_user
from models import User
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

# Define a schema for updating subscription tier.
class SubscriptionUpdate(BaseModel):
    # Restrict allowed tiers using Literal. In a more complete app, you might use an Enum.
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
    return {"id": current_user.id, "email": current_user.email, "subscription_tier": current_user.subscription_tier}
