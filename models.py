from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Relationships
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")

class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    search_query = Column(String, nullable=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    frequency = Column(String, nullable=False, default="daily")  # daily, hourly
    locations = Column(String, nullable=True)
    listing_type = Column(String, nullable=False, default="all")  # all, auction, buy_it_now
    
    # Relationships
    user = relationship("User", back_populates="saved_searches")
