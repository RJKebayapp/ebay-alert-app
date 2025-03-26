
from fastapi import APIRouter, Depends
from models import User
from dependencies import get_current_user

router = APIRouter()

@router.get("/protected")
async def read_protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.email}. This is a protected route!"}
