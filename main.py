from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import sys
import os
import traceback
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Import routers
from auth import router as auth_router
from saved_searches import router as saved_searches_router
from models import Base
from database_config import engine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(saved_searches_router, tags=["Saved Searches"])

# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to the eBay Alert App API!"}

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Return debug information about the environment."""
    import pkg_resources
    
    debug_info = {
        "python_version": sys.version,
        "environment": {k: v for k, v in os.environ.items() 
                      if not k.startswith("_") 
                      and k.lower() not in ("path", "secret", "key", "password", "token")},
        "is_database_configured": bool(os.environ.get("DATABASE_URL")),
        "installed_packages": [f"{p.project_name}=={p.version}" for p in pkg_resources.working_set]
    }
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            debug_info["database_connection_test"] = "Success" if row == 1 else "Failed"
    except Exception as e:
        debug_info["database_connection_error"] = str(e)
        debug_info["database_connection_traceback"] = traceback.format_exc()
    
    return debug_info

@app.on_event("startup")
async def startup_event():
    """Run when the application starts."""
    logger.info("Starting up the application...")
    try:
        # Create tables if they don't exist using the async engine
        async with engine.begin() as conn:
            logger.info("Creating database tables if they don't exist...")
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())
        # Re-raise the exception to prevent the app from starting if critical initialization fails
        raise
