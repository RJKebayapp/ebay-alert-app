from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum

# Enums for schemas
class SearchFrequencyEnum(str, Enum):
    DAILY = "daily"
    HOURLY = "hourly"

class ListingTypeEnum(str, Enum):
    ALL = "all"
    AUCTION = "auction"
    BUY_IT_NOW = "buy_it_now"

# User Schemas
class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: int
    email: str

class TokenDataSchema(BaseModel):
    email: Optional[str] = None

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

# Saved Search Schemas
class SavedSearchCreateSchema(BaseModel):
    search_query: str = Field(..., min_length=1, max_length=200)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    frequency: Optional[SearchFrequencyEnum] = SearchFrequencyEnum.DAILY
    locations: Optional[str] = None
    listing_type: Optional[ListingTypeEnum] = ListingTypeEnum.ALL

class SavedSearchResponseSchema(SavedSearchCreateSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True
