from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import SavedSearch, User
from saved_search_schemas import SavedSearchCreate, SavedSearchOut, SavedSearchUpdate
from database_config import get_async_session
from dependencies import get_current_user

router = APIRouter()

# Tier-based rules configuration
TIER_RULES = {
    "free": {
        "max_searches": 1,
        "max_words": 1,
        "default_frequency": 3600,  # once per hour
        "allowed_locations": ["USA"]
    },
    "mid": {
        "max_searches": 3,
        "max_words": 2,
        "default_frequency": 1800,  # every 30 minutes
        "max_locations": 5
    },
    "top": {
        "max_searches": 25,
        "max_words": 5,
        "default_frequency": 30,    # every 30 seconds
        "max_locations": None
    }
}

@router.get("/saved-searches", response_model=list[SavedSearchOut])
async def get_saved_searches(
    current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(SavedSearch).where(SavedSearch.user_id == current_user.id))
    searches = result.scalars().all()
    return searches

@router.post("/saved-searches", response_model=SavedSearchOut)
async def create_saved_search(
    search: SavedSearchCreate, 
    current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    tier = (current_user.subscription_tier or "free").lower()
    rules = TIER_RULES.get(tier, TIER_RULES["free"])

    # Check existing saved searches count
    result = await session.execute(select(SavedSearch).where(SavedSearch.user_id == current_user.id))
    existing_searches = result.scalars().all()
    if len(existing_searches) >= rules["max_searches"]:
        raise HTTPException(
            status_code=400, 
            detail=f"{tier.capitalize()} tier allows only {rules['max_searches']} saved search(es)."
        )

    # Validate search query word count
    word_count = len(search.search_query.split())
    if word_count > rules["max_words"]:
        raise HTTPException(
            status_code=400, 
            detail=f"{tier.capitalize()} tier allows up to {rules['max_words']} word(s) in search query."
        )

    # Override frequency with tier's default frequency
    frequency = rules["default_frequency"]

    # Validate locations (assuming locations are provided as comma-separated string)
    locations = []
    if search.locations:
        locations = [loc.strip() for loc in search.locations.split(",") if loc.strip()]
    if tier == "free":
        if any(loc.upper() != "USA" for loc in locations):
            raise HTTPException(
                status_code=400, 
                detail="Free tier only supports searches in USA."
            )
    elif tier == "mid":
        if len(locations) > rules["max_locations"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Mid tier supports up to {rules['max_locations']} locations."
            )

    new_search = SavedSearch(
        user_id=current_user.id,
        search_query=search.search_query,
        min_price=search.min_price,
        max_price=search.max_price,
        frequency=frequency,
        locations=",".join(locations) if locations else None,
        listing_type=search.listing_type or "Buy It Now New"
    )
    session.add(new_search)
    await session.commit()
    await session.refresh(new_search)
    return new_search

@router.put("/saved-searches/{search_id}", response_model=SavedSearchOut)
async def update_saved_search(
    search_id: int, 
    search_update: SavedSearchUpdate, 
    current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(SavedSearch).where(SavedSearch.id == search_id, SavedSearch.user_id == current_user.id)
    )
    saved_search = result.scalars().first()
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found.")

    tier = (current_user.subscription_tier or "free").lower()
    rules = TIER_RULES.get(tier, TIER_RULES["free"])

    if search_update.search_query:
        word_count = len(search_update.search_query.split())
        if word_count > rules["max_words"]:
            raise HTTPException(
                status_code=400, 
                detail=f"{tier.capitalize()} tier allows up to {rules['max_words']} word(s) in search query."
            )
        saved_search.search_query = search_update.search_query

    if search_update.min_price is not None:
        saved_search.min_price = search_update.min_price
    if search_update.max_price is not None:
        saved_search.max_price = search_update.max_price

    if search_update.locations:
        locations = [loc.strip() for loc in search_update.locations.split(",") if loc.strip()]
        if tier == "free" and any(loc.upper() != "USA" for loc in locations):
            raise HTTPException(status_code=400, detail="Free tier only supports searches in USA.")
        elif tier == "mid" and len(locations) > rules["max_locations"]:
            raise HTTPException(status_code=400, detail=f"Mid tier supports up to {rules['max_locations']} locations.")
        saved_search.locations = ",".join(locations)

    # Enforce tier's default frequency (cannot be updated by user)
    saved_search.frequency = rules["default_frequency"]

    if search_update.listing_type:
        saved_search.listing_type = search_update.listing_type

    session.add(saved_search)
    await session.commit()
    await session.refresh(saved_search)
    return saved_search

@router.delete("/saved-searches/{search_id}", status_code=204)
async def delete_saved_search(
    search_id: int, 
    current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(SavedSearch).where(SavedSearch.id == search_id, SavedSearch.user_id == current_user.id)
    )
    saved_search = result.scalars().first()
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found.")
    await session.delete(saved_search)
    await session.commit()
    return None
