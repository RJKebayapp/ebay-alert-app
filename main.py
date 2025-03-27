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
from sqlalchemy.future import select

# Import routers and configurations
from auth import router as auth_router
from protected_routes import router as protected_router
from user_routes import router as user_router
from saved_search_routes import router as saved_search_router
from alert_scheduler import check_saved_searches
from models import Base, User
from database_config import engine, AsyncSessionLocal

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="eBay Alert App",
    description="An API for managing eBay search alerts",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(protected_router, tags=["Protected Routes"])
app.include_router(user_router, tags=["User Management"])
app.include_router(saved_search_router, tags=["Saved Searches"])

# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy errors."""
    logger.error(f"SQLAlchemy error: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error", "error": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    error_msg = f"Unhandled exception: {str(exc)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)}
    )

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

# Diagnostic endpoint
@app.get("/diagnostic")
async def diagnostic_check():
    """Diagnostic endpoint to test database operations directly."""
    results = {}
    
    # Test database connection
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            results["database_connection"] = "Success" if row == 1 else "Failed"
    except Exception as e:
        results["database_connection_error"] = str(e)
        logger.error(f"Database connection error: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Try to create a test user directly (will be rolled back)
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Check if test user exists
                test_email = "diagnostic_test@example.com"
                query = select(User).where(User.email == test_email)
                result = await session.execute(query)
                test_user = result.scalars().first()
                
                if test_user:
                    results["test_user_exists"] = True
                    results["test_user_id"] = test_user.id
                else:
                    results["test_user_exists"] = False
                
                # Try to create a user object without committing
                test_user = User(
                    email=test_email,
                    hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 'testpassword'
                )
                session.add(test_user)
                # Roll back so we don't actually create the user
                await session.rollback()
                results["user_object_creation"] = "Success"
    except Exception as e:
        results["user_creation_error"] = str(e)
        logger.error(f"Error testing user creation: {str(e)}")
        logger.error(traceback.format_exc())
    
    # List all users (just count)
    try:
        async with AsyncSessionLocal() as session:
            query = select(User)
            result = await session.execute(query)
            users = result.scalars().all()
            results["user_count"] = len(list(users))
    except Exception as e:
        results["user_list_error"] = str(e)
        logger.error(f"Error listing users: {str(e)}")
        logger.error(traceback.format_exc())
    
    return results

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

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
    """Run when the application shuts down."""
    logger.info("Shutting down the application...")
    # Add any cleanup code here if needed
