
from fastapi import FastAPI
from .auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the eBay Alert API"}
