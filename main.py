
from fastapi import FastAPI
from auth import router as auth_router  # Import the router from auth.py

app = FastAPI()

# Include the router from auth.py
app.include_router(auth_router)
