from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class SavedSearchBase(BaseModel):
    search_query: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    frequency: Optional[str] = "daily"  # daily, hourly, etc.
    locations: Optional[str] = None
    listing_type: Optional[str] = "all"  # all, auction, buy_it_now

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(SavedSearchBase):
    search_query: Optional[str] = None
    
class SavedSearchResponse(SavedSearchBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str
