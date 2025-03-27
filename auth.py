# auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import User
from schemas import UserCreateSchema  # Make sure your schemas.py defines UserCreateSchema
from dependencies import get_db  # Dependency that returns a valid DB session
from email_utils import send_registration_email
from utils import hash_password  # A utility function to hash passwords

router = APIRouter()

@router.post("/register")
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash the password and create a new user record
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to load any auto-generated fields

    # Send confirmation email
    send_registration_email(user.email)
    
    return {"message": "User registered successfully"}
