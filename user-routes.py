from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
import traceback

from models import User
from schemas import UserUpdate, UserOut
from database_config import get_async_session
from auth import get_current_user
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up logging
logger = logging.getLogger(__name__)

@router.get("/users/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    try:
        return current_user
    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )

@router.put("/users/me", response_model=UserOut)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update current user information."""
    try:
        # Update user fields
        if user_update.email is not None:
            current_user.email = user_update.email
        
        # Update password if provided
        if user_update.password is not None:
            current_user.hashed_password = pwd_context.hash(user_update.password)
        
        # Commit changes
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        
        return current_user
    except SQLAlchemyError as e:
        logger.error(f"Database error updating user: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating user: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Optional: Add delete account functionality
@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete current user account."""
    try:
        await db.delete(current_user)
        await db.commit()
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting user: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting user: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
