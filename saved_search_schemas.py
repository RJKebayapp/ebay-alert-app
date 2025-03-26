from pydantic import BaseModel
from typing import Optional

class SavedSearchBase(BaseModel):
    search_query: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    locations: Optional[str] = None  # Comma-separated list of locations
    listing_type: Optional[str] = "Buy It Now New"

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(SavedSearchBase):
    pass

class SavedSearchOut(SavedSearchBase):
    id: int
    user_id: int
    frequency: int

    class Config:
        orm_mode = True
