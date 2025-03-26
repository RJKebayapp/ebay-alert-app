from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models import Base  # Ensure this imports the same Base used in your main models file

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

    user = relationship("User", back_populates="saved_searches")
