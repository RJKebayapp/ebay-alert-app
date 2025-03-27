from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# Existing schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# New schemas for saved searches
class SavedSearchCreate(BaseModel):
    search_query: str = Field(..., min_length=1, max_length=200)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    frequency: Optional[str] = Field(default="daily", pattern="^(daily|hourly)$")
    locations: Optional[str] = None
    listing_type: Optional[str] = Field(default="all", pattern="^(all|auction|buy_it_now)$")

class SavedSearchResponse(SavedSearchCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
