
from fastapi import FastAPI
from auth import router as auth_router
from utils import hash_password, generate_jwt_token, get_db  # Ensure utils are imported here

app = FastAPI()

# Basic root endpoint to ensure the server responds to the root request
@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

# Include the authentication routes
app.include_router(auth_router)
    