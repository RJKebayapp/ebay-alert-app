
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from email_utils import send_registration_email  # Assuming this function is already implemented
from models import User
from utils import hash_password, generate_jwt_token, get_db  # Assuming these are defined elsewhere

router = APIRouter()

# Register User Endpoint
@router.post("/register")
async def register_user(
    email: str,
    password: str,
    telegram_chat_id: str,
    email_alerts_enabled: bool,
    telegram_alerts_enabled: bool,
    db: Session = Depends(get_db),  # Assuming you have a function to get db session
):
    # Hash password
    hashed_password = hash_password(password)  # Assuming hash_password is defined elsewhere
    
    try:
        # Create the user object
        user = User(
            email=email,
            hashed_password=hashed_password,
            subscription_tier="FREE",  # Example, adjust as needed
        )
        
        # Add user to the session
        db.session.add(user)
        db.session.commit()  # Commit here to ensure user is saved first
        
        # Send registration email after commit
        send_registration_email(email)  # Assuming this function is in email_utils.py
        
        # Return success response
        return {"token": generate_jwt_token(user)}  # Example for JWT token generation
    
    except Exception as e:
        db.session.rollback()  # Rollback on failure
        raise HTTPException(status_code=500, detail=str(e))  # Provide detailed error message
