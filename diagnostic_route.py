# Add this diagnostic endpoint to your main.py file

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
