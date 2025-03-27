from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    """Enum representing different subscription tiers for users."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class SearchFrequency(enum.Enum):
    """Enum for search update frequencies."""
    DAILY = "daily"
    HOURLY = "hourly"

class ListingType(enum.Enum):
    """Enum for listing types."""
    ALL = "all"
    AUCTION = "auction"
    BUY_IT_NOW = "buy_it_now"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Added subscription tier to resolve constraint
    subscription_tier = Column(Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    
    # Relationships
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")

class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    search_query = Column(String, nullable=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    
    # Use Enum for frequency
    frequency = Column(Enum(SearchFrequency), nullable=False, default=SearchFrequency.DAILY)
    
    locations = Column(String, nullable=True)
    
    # Use Enum for listing type
    listing_type = Column(Enum(ListingType), nullable=False, default=ListingType.ALL)
    
    # Relationships
    user = relationship("User", back_populates="saved_searches")
