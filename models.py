
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    subscription_tier = Column(String, nullable=False, default="free")
    
    # Relationship to saved searches
    saved_searches = relationship("SavedSearch", back_populates="user")

class SavedSearch(Base):
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_query = Column(String, nullable=False)
    min_price = Column(Integer, nullable=True)
    max_price = Column(Integer, nullable=True)
    frequency = Column(Integer, nullable=False)  # in seconds
    locations = Column(String, nullable=True)      # comma-separated list of locations
    listing_type = Column(String, default="Buy It Now New", nullable=False)
    
    # Relationship back to the user
    user = relationship("User", back_populates="saved_searches")
