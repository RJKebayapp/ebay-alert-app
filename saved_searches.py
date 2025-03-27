from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from models import SavedSearch, User
from schemas import SavedSearchCreate, SavedSearchResponse
from auth import get_current_user
from database_config import get_async_session

router = APIRouter()

@router.post("/saved-searches", response_model=SavedSearchResponse)
async def create_saved_search(
    saved_search: SavedSearchCreate, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new saved search for the current user."""
    try:
        # Create new saved search
        new_search = SavedSearch(
            user_id=current_user.id,
            search_query=saved_search.search_query,
            min_price=saved_search.min_price,
            max_price=saved_search.max_price,
            locations=saved_search.locations,
            frequency=saved_search.frequency or "daily",
            listing_type=saved_search.listing_type or "all"
        )
        
        # Add to database
        db.add(new_search)
        await db.commit()
        await db.refresh(new_search)
        
        return new_search
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/saved-searches", response_model=list[SavedSearchResponse])
async def get_user_saved_searches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Retrieve all saved searches for the current user."""
    try:
        # Query saved searches for the current user
        query = select(SavedSearch).where(SavedSearch.user_id == current_user.id)
        result = await db.execute(query)
        saved_searches = result.scalars().all()
        
        return saved_searches
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/saved-searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a specific saved search for the current user."""
    try:
        # Find the saved search
        query = select(SavedSearch).where(
            (SavedSearch.id == search_id) & (SavedSearch.user_id == current_user.id)
        )
        result = await db.execute(query)
        saved_search = result.scalar_one_or_none()
        
        # Check if search exists and belongs to user
        if not saved_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
        
        # Delete the search
        await db.delete(saved_search)
        await db.commit()
        
        return None
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
