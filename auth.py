
# auth.py

# Assuming you have a function to handle registration
def register_user(email, password, telegram_chat_id, email_alerts_enabled, telegram_alerts_enabled):
    # Hash password
    hashed_password = hash_password(password)  # assuming hash_password is defined elsewhere
    
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
