from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="ebay_app.env.txt")

# Construct DATABASE_URL dynamically from environment variables
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', '')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}/"
    f"{os.getenv('POSTGRES_DB', 'ebay_app')}"
)

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Detailed logging (set to False in production)
    future=True  # Enable 2.0 style SQLAlchemy features
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Declarative base for ORM models
Base = declarative_base()

# Async database session dependency
async def get_db():
    """
    Dependency function to get async database session.
    Yields a database session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
