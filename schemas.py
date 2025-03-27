from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

# Use str instead of EmailStr to avoid validation issues
class UserBase(BaseModel):
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        # Simple email validation
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserUpdate(UserBase):
    email: Optional[str] = None
    password: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(UserBase):
    password: str

class UserOut(UserBase):
    id: int

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
