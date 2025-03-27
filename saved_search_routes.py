from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
import traceback

from models import User, SavedSearch
from schemas import SavedSearchCreate, SavedSearchUpdate, SavedSearchResponse
from dependencies import get_current_user
from database_config import get_async_session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/saved-searches", response_model=SavedSearchResponse)
async def create_saved_search(
    saved_search: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new saved search for the current user."""
    try:
        new_saved_search = SavedSearch(
            user_id=current_user.id,
            search_query=saved_search.search_query,
            min_price=saved_search.min_price,
            max_price=saved_search.max_price,
            frequency=saved_search.frequency,
            locations=saved_search.locations,
            listing_type=saved_search.listing_type
        )
        
        db.add(new_saved_search)
        await db.commit()
        await db.refresh(new_saved_search)
        
        return new_saved_search
    except SQLAlchemyError as e:
        logger.error(f"Database error creating saved search: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating saved search: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/saved-searches", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all saved searches for the current user."""
    try:
        result = await db.execute(
            select(SavedSearch).where(SavedSearch.user_id == current_user.id)
        )
        saved_searches = result.scalars().all()
        return saved_searches
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving saved searches: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving saved searches: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/saved-searches/{saved_search_id}", response_model=SavedSearchResponse)
async def get_saved_search(
    saved_search_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get a specific saved search by ID."""
    try:
        result = await db.execute(
            select(SavedSearch).where(
                SavedSearch.id == saved_search_id,
                SavedSearch.user_id == current_user.id
            )
        )
        saved_search = result.scalars().first()
        
        if saved_search is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
            
        return saved_search
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving saved search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving saved search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.put("/saved-searches/{saved_search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    saved_search_id: int,
    saved_search_update: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a specific saved search by ID."""
    try:
        result = await db.execute(
            select(SavedSearch).where(
                SavedSearch.id == saved_search_id,
                SavedSearch.user_id == current_user.id
            )
        )
        saved_search = result.scalars().first()
        
        if saved_search is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
            
        # Update fields if provided
        if saved_search_update.search_query is not None:
            saved_search.search_query = saved_search_update.search_query
        if saved_search_update.min_price is not None:
            saved_search.min_price = saved_search_update.min_price
        if saved_search_update.max_price is not None:
            saved_search.max_price = saved_search_update.max_price
        if saved_search_update.frequency is not None:
            saved_search.frequency = saved_search_update.frequency
        if saved_search_update.locations is not None:
            saved_search.locations = saved_search_update.locations
        if saved_search_update.listing_type is not None:
            saved_search.listing_type = saved_search_update.listing_type
            
        # Commit changes
        db.add(saved_search)
        await db.commit()
        await db.refresh(saved_search)
        
        return saved_search
    except SQLAlchemyError as e:
        logger.error(f"Database error updating saved search: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating saved search: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.delete("/saved-searches/{saved_search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    saved_search_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a specific saved search by ID."""
    try:
        result = await db.execute(
            select(SavedSearch).where(
                SavedSearch.id == saved_search_id,
                SavedSearch.user_id == current_user.id
            )
        )
        saved_search = result.scalars().first()
        
        if saved_search is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
            
        # Delete the saved search
        await db.delete(saved_search)
        await db.commit()
        
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting saved search: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting saved search: {str(e)}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
