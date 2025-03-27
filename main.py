# main.py

from fastapi import FastAPI
from auth import router as auth_router

app = FastAPI()

# Include the auth routes in the FastAPI application
app.include_router(auth_router)
