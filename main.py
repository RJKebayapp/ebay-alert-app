from fastapi import FastAPI, HTTPException, Depends, Request
import asyncio
import logging
import sys
import os
import traceback
from auth import router as auth_router
from protected_routes import router as protected_router
from user_routes import router as user_router
from saved_search_routes import router as saved_search_router
from alert_scheduler import check_saved_searches
from models import Base
from database_config import engine
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include all routers
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(user_router)
app.include_router(saved_search_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Unhandled exception: {str(exc)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    return {"detail": "Internal server error", "error": str(exc)}

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from the eBay Alert App!"}

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Return debug information about the environment"""
    import pkg_resources
    
    # Collect basic information
    debug_info = {
        "python_version": sys.version,
        "environment": {k: v for k, v in os.environ.items() 
                      if not k.startswith("_") 
                      and k.lower() not in ("path", "secret", "key", "password", "token")},
        "is_database_configured": bool(os.environ.get("DATABASE_URL")),
        "installed_packages": [f"{p.project_name}=={p.version}" for p in pkg_resources.working_set]
    }
    
    # Test database connection
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            debug_info["database_connection_test"] = "Success" if row == 1 else "Failed"
    except Exception as e:
        debug_info["database_connection_error"] = str(e)
        debug_info["database_connection_traceback"] = traceback.format_exc()
    
    return debug_info

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")
    try:
        # Create tables if they don't exist using the async engine
        async with engine.begin() as conn:
            logger.info("Creating database tables if they don't exist...")
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully.")
        
        # Short delay to be sure everything is set
        await asyncio.sleep(2)
        
        # Launch the background task for checking saved searches
        logger.info("Starting background task for checking saved searches...")
        asyncio.create_task(check_saved_searches())
        
        logger.info("Application startup completed successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())
        # Re-raise the exception to prevent the app from starting if critical initialization fails
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
    # Add any cleanup code here if needed
