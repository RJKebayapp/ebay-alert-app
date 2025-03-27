from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import traceback

from models import User
from dependencies import get_current_user
from database_config import get_async_session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """A protected route that requires authentication."""
    try:
        return {
            "message": "You have access to this protected route",
            "user_email": current_user.email
        }
    except Exception as e:
        logger.error(f"Error in protected route: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
