from fastapi import FastAPI
import asyncio
from auth import router as auth_router
from protected_routes import router as protected_router
from user_routes import router as user_router
from saved_search_routes import router as saved_search_router
from alert_scheduler import check_saved_searches
from models import Base
from database_config import engine

app = FastAPI()

# Include all routers
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(user_router)
app.include_router(saved_search_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from the eBay Alert App!"}

@app.on_event("startup")
async def startup_event():
    # Create tables if they don't exist using the async engine
    await engine.run_sync(Base.metadata.create_all)
    # Short delay to be sure everything is set
    await asyncio.sleep(2)
    # Launch the background task for checking saved searches
    asyncio.create_task(check_saved_searches())

